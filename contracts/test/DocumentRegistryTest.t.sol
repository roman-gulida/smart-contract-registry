// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {Test} from "forge-std/Test.sol";
import {DocumentRegistry} from "src/DocumentRegistry.sol";
import {DeployDocumentRegistry} from "script/DeployDocumentRegistry.s.sol";

contract DocumentRegistryTest is Test {
    DocumentRegistry public docRegistry;

    address public immutable USER = makeAddr("user");
    bytes32 public constant INVALID_HASH = bytes32(0);
    bytes32 public constant DOC_HASH = keccak256(abi.encode("document"));
    bytes32 public constant MODEL_HASH = keccak256(abi.encode("model"));

    function setUp() external {
        DeployDocumentRegistry deployer = new DeployDocumentRegistry();
        docRegistry = deployer.run();
    }

    function testRegisterRevertsOnInvalidDocHash() external {
        vm.expectRevert(DocumentRegistry.InvalidDocumentHash.selector);
        docRegistry.registerClassification(
            INVALID_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );
    }

    function testRegisterRevertsOnInvalidModelHash() external {
        vm.expectRevert(DocumentRegistry.InvalidModelHash.selector);
        docRegistry.registerClassification(
            DOC_HASH,
            INVALID_HASH,
            DocumentRegistry.Decision.HR
        );
    }

    function testRegisterRevertsIfDocumentAlreadyRegistered() external {
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );
        vm.expectRevert(DocumentRegistry.DocumentAlreadyRegistered.selector);
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );
    }

    function testRegisterRecordsClassification() external {
        vm.prank(USER);
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );

        (
            bytes32 docHash,
            bytes32 modelHash,
            DocumentRegistry.Decision decision,
            uint256 timestamp,
            address uploader
        ) = docRegistry.classifications(DOC_HASH);

        assert(docHash == DOC_HASH);
        assert(modelHash == MODEL_HASH);
        assert(decision == DocumentRegistry.Decision.HR);
        assert(timestamp > 0);
        assert(uploader == USER);
    }

    function testRegisterEmitsEvent() external {
        vm.expectEmit(true, true, true, false, address(docRegistry));
        emit DocumentRegistry.ClassificationRegistered(
            DOC_HASH,
            DocumentRegistry.Decision.HR,
            USER
        );
        vm.prank(USER);
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );
    }

    function testRegisterRecordsRecordsDocHashes() external {
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );

        bytes32 actualDocHash = docRegistry.documentHashes(0);

        assert(actualDocHash == DOC_HASH);
        assert(docRegistry.documentExists(actualDocHash) == true);
    }

    function testGetClassificationRevertsIfDocumentNotFound() external {
        vm.expectRevert(
            abi.encodeWithSelector(
                DocumentRegistry.DocumentNotFound.selector,
                DOC_HASH
            )
        );
        docRegistry.getClassification(DOC_HASH);
    }

    function testGetClassificationReturnsClassification() external {
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );

        (
            bytes32 expectedDocHash,
            bytes32 expectedModelHash,
            DocumentRegistry.Decision expectedDecision,
            uint256 expectedTimestamp,
            address expectedUploader
        ) = docRegistry.classifications(DOC_HASH);

        (
            bytes32 actualDocHash,
            bytes32 actualModelHash,
            DocumentRegistry.Decision actualDecision,
            uint256 actualTimestamp,
            address actualUploader
        ) = docRegistry.getClassification(DOC_HASH);

        assert(expectedDocHash == actualDocHash);
        assert(expectedModelHash == actualModelHash);
        assert(expectedDecision == actualDecision);
        assert(expectedTimestamp == actualTimestamp);
        assert(expectedUploader == actualUploader);
    }

    function testGetTotalDocumentsReturnsAccurateAmountOfDocs() external {
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );

        bytes32 DOC_HASH_2 = keccak256(abi.encode("document_2"));
        bytes32 MODEL_HASH_2 = keccak256(abi.encode("model_2"));

        docRegistry.registerClassification(
            DOC_HASH_2,
            MODEL_HASH_2,
            DocumentRegistry.Decision.SALARY
        );

        assert(docRegistry.getTotalDocuments() == 2);
    }

    function testGetDocumentHashRevertsOnIndexOutOfBounds() external {
        vm.expectRevert(DocumentRegistry.IndexOutOfBounds.selector);
        docRegistry.getDocumentHashByIndex(0);
    }

    function testGetDocumentHashReturnsDocumentByIndex() external {
        docRegistry.registerClassification(
            DOC_HASH,
            MODEL_HASH,
            DocumentRegistry.Decision.HR
        );

        bytes32 actualDocHash = docRegistry.getDocumentHashByIndex(0);

        assert(DOC_HASH == actualDocHash);
    }

    // fuzz test
    function testFuzzRegisterClassification(
        bytes32 docHash,
        bytes32 modelHash,
        uint8 decisionRaw
    ) external {
        vm.assume(docHash > bytes32(0));
        vm.assume(modelHash > bytes32(0));
        vm.assume(decisionRaw <= uint8(DocumentRegistry.Decision.HR));

        DocumentRegistry.Decision decision = DocumentRegistry.Decision(
            decisionRaw
        );

        docRegistry.registerClassification(docHash, modelHash, decision);

        assert(docRegistry.documentExists(docHash));
    }
}
