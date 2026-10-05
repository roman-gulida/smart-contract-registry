// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

contract DocumentRegistry {
    error InvalidDocumentHash();
    error InvalidModelHash();
    error DocumentAlreadyRegistered();
    error DocumentNotFound(bytes32 docHash);
    error IndexOutOfBounds();

    struct Classification {
        bytes32 docHash;
        bytes32 modelHash;
        Decision decision;
        uint256 timestamp;
        address uploader;
    }

    enum Decision {
        LOGISTICS,
        SALARY,
        FINANCE,
        LEGAL,
        HR
    }

    mapping(bytes32 docHash => Classification) public classifications;
    bytes32[] public documentHashes;
    mapping(bytes32 docHash => bool exists) public documentExists;

    event ClassificationRegistered(
        bytes32 indexed docHash,
        Decision indexed decision,
        address indexed uploader
    );

    /**
     * @dev Register a new document classification
     * @param _docHash Hash of the document
     * @param _modelHash Hash of the ML model used
     * @param _decision Classification decision ("logistics" | "salary" | "finance" | "legal" | "hr")
     */
    function registerClassification(
        bytes32 _docHash,
        bytes32 _modelHash,
        Decision _decision
    ) public {
        if (_docHash == bytes32(0)) revert InvalidDocumentHash();
        if (_modelHash == bytes32(0)) revert InvalidModelHash();
        if (documentExists[_docHash]) revert DocumentAlreadyRegistered();

        classifications[_docHash] = Classification({
            docHash: _docHash,
            modelHash: _modelHash,
            decision: _decision,
            timestamp: block.timestamp,
            uploader: msg.sender
        });

        documentHashes.push(_docHash);
        documentExists[_docHash] = true;
        emit ClassificationRegistered(_docHash, _decision, msg.sender);
    }

    /**
     * @dev Get classification for a document
     * @param _docHash Hash of the document
     */
    function getClassification(
        bytes32 _docHash
    )
        public
        view
        returns (
            bytes32 docHash,
            bytes32 modelHash,
            Decision decision,
            uint256 timestamp,
            address uploader
        )
    {
        if (!documentExists[_docHash]) revert DocumentNotFound(_docHash);
        Classification memory c = classifications[_docHash];
        return (c.docHash, c.modelHash, c.decision, c.timestamp, c.uploader);
    }

    /**
     * @dev Get total number of registered documents
     */
    function getTotalDocuments() public view returns (uint256) {
        return documentHashes.length;
    }

    /**
     * @dev Get document hash by index
     */
    function getDocumentHashByIndex(
        uint256 index
    ) public view returns (bytes32) {
        if (index >= documentHashes.length) revert IndexOutOfBounds();
        return documentHashes[index];
    }
}
