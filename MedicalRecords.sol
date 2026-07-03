// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalRecords {
    
    struct Prediction {
        string patientId;
        string riskLevel;
        uint256 confidence;
        string aiAdvice;
        uint256 timestamp;
    }

    mapping(string => Prediction[]) private patientRecords;

    event RecordStored(string patientId, string riskLevel, uint256 timestamp);

    function storePrediction(
        string memory patientId,
        string memory riskLevel,
        uint256 confidence,
        string memory aiAdvice
    ) public {
        Prediction memory newRecord = Prediction({
            patientId: patientId,
            riskLevel: riskLevel,
            confidence: confidence,
            aiAdvice: aiAdvice,
            timestamp: block.timestamp
        });

        patientRecords[patientId].push(newRecord);
        
        emit RecordStored(patientId, riskLevel, block.timestamp);
    }

    function getPatientHistory(string memory patientId) 
        public view returns (Prediction[] memory) {
        return patientRecords[patientId];
    }

    function getRecordCount(string memory patientId) 
        public view returns (uint256) {
        return patientRecords[patientId].length;
    }
}