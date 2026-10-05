// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {Script} from "forge-std/Script.sol";
import {DocumentRegistry} from "src/DocumentRegistry.sol";

contract DeployDocumentRegistry is Script {
    function run() external returns (DocumentRegistry) {
        vm.startBroadcast();
        DocumentRegistry docRegistry = new DocumentRegistry();
        vm.stopBroadcast();
        return docRegistry;
    }
}
