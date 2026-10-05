"""
Blockchain Service
Interfaces with the DocumentRegistry Solidity contract via web3.py
"""

import logging
from functools import lru_cache
from typing import Optional

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)

#  Contract ABI
CONTRACT_ABI = [
    {
        "name": "registerClassification",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "_docHash", "type": "bytes32"},
            {"name": "_modelHash", "type": "bytes32"},
            {"name": "_decision", "type": "uint8"},
        ],
        "outputs": [],
    },
    {
        "name": "getClassification",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "_docHash", "type": "bytes32"}],
        "outputs": [
            {"name": "docHash", "type": "bytes32"},
            {"name": "modelHash", "type": "bytes32"},
            {"name": "decision", "type": "uint8"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "uploader", "type": "address"},
        ],
    },
    {
        "name": "getTotalDocuments",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "documentExists",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "docHash", "type": "bytes32"}],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "ClassificationRegistered",
        "type": "event",
        "inputs": [
            {"name": "docHash", "type": "bytes32", "indexed": True},
            {"name": "decision", "type": "uint8", "indexed": True},
            {"name": "uploader", "type": "address", "indexed": True},
        ],
    },
]

DECISION_NAMES = ["LOGISTICS", "SALARY", "FINANCE", "LEGAL", "HR"]


class BlockchainService:
    def __init__(self):
        self.w3: Optional[Web3] = None
        self.contract = None
        self.account = None
        self._connect()

    def _connect(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

            if not self.w3.is_connected():
                logger.warning(
                    "Cannot connect to blockchain node at %s",
                    settings.WEB3_PROVIDER_URL,
                )
                self.w3 = None
                return

            if settings.DEPLOYER_PRIVATE_KEY:
                self.account = self.w3.eth.account.from_key(
                    settings.DEPLOYER_PRIVATE_KEY
                )
                logger.info("Using account: %s", self.account.address)

            if settings.CONTRACT_ADDRESS:
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
                    abi=CONTRACT_ABI,
                )
                logger.info("Contract loaded at %s", settings.CONTRACT_ADDRESS)
            else:
                logger.warning("CONTRACT_ADDRESS not set. Blockchain writes disabled.")

        except Exception as e:
            logger.error("Blockchain connection error: %s", e)
            self.w3 = None

    @property
    def is_connected(self) -> bool:
        try:
            return self.w3 is not None and self.w3.is_connected()
        except Exception:
            return False

    @property
    def is_ready(self) -> bool:
        """Connected + contract loaded + account available"""
        return (
            self.is_connected and self.contract is not None and self.account is not None
        )

    def _hex_to_bytes32(self, hex_str: str) -> bytes:
        """Convert 0x-prefixed hex string to 32-byte value"""
        clean = hex_str.removeprefix("0x")
        return bytes.fromhex(clean.zfill(64))

    def register_classification(
        self,
        doc_hash: str,
        model_hash: str,
        decision_index: int,
    ) -> dict:
        """
        Send registerClassification transaction to the contract.

        Args:
            doc_hash:       "0x..." hex string (SHA-256 of PDF bytes)
            model_hash:     "0x..." hex string
            decision_index: 0-4 matching Solidity enum Decision

        Returns:
            {"tx_hash": "0x...", "block": 42, "uploader": "0x...", "status": 1}
        """
        if not self.is_ready:
            raise RuntimeError(
                "Blockchain service not ready. Check WEB3_PROVIDER_URL and CONTRACT_ADDRESS."
            )

        doc_bytes32 = self._hex_to_bytes32(doc_hash)
        model_bytes32 = self._hex_to_bytes32(model_hash)

        nonce = self.w3.eth.get_transaction_count(self.account.address)

        tx = self.contract.functions.registerClassification(
            doc_bytes32,
            model_bytes32,
            decision_index,
        ).build_transaction(
            {
                "from": self.account.address,
                "nonce": nonce,
                "gasPrice": self.w3.eth.gas_price,
            }
        )

        signed = self.w3.eth.account.sign_transaction(
            tx, private_key=settings.DEPLOYER_PRIVATE_KEY
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "tx_hash": receipt.transactionHash.hex(),
            "block": receipt.blockNumber,
            "uploader": self.account.address,
            "status": receipt.status,  # 1 = success, 0 = reverted
        }

    def get_classification(self, doc_hash: str) -> Optional[dict]:
        """
        Read a classification from the contract (no gas needed).
        Returns None if not found on chain.
        """
        if not self.is_ready:
            return None

        try:
            doc_bytes32 = self._hex_to_bytes32(doc_hash)
            exists = self.contract.functions.documentExists(doc_bytes32).call()
            if not exists:
                return None

            result = self.contract.functions.getClassification(doc_bytes32).call()
            doc_h, model_h, decision, timestamp, uploader = result

            return {
                "doc_hash": "0x" + doc_h.hex(),
                "model_hash": "0x" + model_h.hex(),
                "decision": DECISION_NAMES[decision],
                "decision_index": decision,
                "timestamp": timestamp,
                "uploader": uploader,
            }
        except Exception as e:
            logger.error("getClassification error: %s", e)
            return None

    def get_total_documents(self) -> Optional[int]:
        if not self.is_ready:
            return None
        try:
            return self.contract.functions.getTotalDocuments().call()
        except Exception:
            return None


@lru_cache(maxsize=1)
def get_blockchain_service() -> BlockchainService:
    return BlockchainService()
