"""
AetherEdge MLOps - MLflow Configuration and Model Management
Manages ML model lifecycle, versioning, and deployment
"""

import os
import mlflow
import mlflow.sklearn
import mlflow.keras
import mlflow.pytorch
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MLflowModelManager:
    """MLflow-based model lifecycle management for AetherEdge"""
    
    def __init__(self, tracking_uri: str = "http://mlflow:5000"):
        """Initialize MLflow model manager"""
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient(tracking_uri)
        
    def create_experiment(self, experiment_name: str, artifact_location: str = None) -> str:
        """Create or get MLflow experiment"""
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment:
                return experiment.experiment_id
            else:
                return mlflow.create_experiment(
                    name=experiment_name,
                    artifact_location=artifact_location
                )
        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            raise
    
    def log_model(self, 
                  model: Any,
                  model_name: str,
                  experiment_name: str,
                  parameters: Dict[str, Any],
                  metrics: Dict[str, float],
                  artifacts: Dict[str, str] = None,
                  model_framework: str = "sklearn") -> str:
        """Log model to MLflow"""
        
        experiment_id = self.create_experiment(experiment_name)
        
        with mlflow.start_run(experiment_id=experiment_id) as run:
            # Log parameters
            mlflow.log_params(parameters)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log artifacts
            if artifacts:
                for name, path in artifacts.items():
                    mlflow.log_artifact(path, name)
            
            # Log model based on framework
            if model_framework == "sklearn":
                mlflow.sklearn.log_model(model, model_name)
            elif model_framework == "keras":
                mlflow.keras.log_model(model, model_name)
            elif model_framework == "pytorch":
                mlflow.pytorch.log_model(model, model_name)
            else:
                mlflow.log_artifact(model, model_name)
            
            return run.info.run_id
    
    def register_model(self, model_name: str, run_id: str, model_version: str = None) -> str:
        """Register model in MLflow Model Registry"""
        try:
            model_uri = f"runs:/{run_id}/{model_name}"
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=model_name
            )
            return model_version.version
        except Exception as e:
            logger.error(f"Error registering model: {e}")
            raise
    
    def promote_model(self, model_name: str, version: str, stage: str) -> None:
        """Promote model to different stage (Staging, Production, Archived)"""
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
                archive_existing_versions=stage == "Production"
            )
            logger.info(f"Model {model_name} v{version} promoted to {stage}")
        except Exception as e:
            logger.error(f"Error promoting model: {e}")
            raise
    
    def load_model(self, model_name: str, stage: str = "Production"):
        """Load model from MLflow Model Registry"""
        try:
            model_uri = f"models:/{model_name}/{stage}"
            return mlflow.pyfunc.load_model(model_uri)
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def get_model_metrics(self, model_name: str, stage: str = "Production") -> Dict[str, Any]:
        """Get metrics for a specific model version"""
        try:
            latest_version = self.client.get_latest_versions(
                model_name, stages=[stage]
            )[0]
            
            run = self.client.get_run(latest_version.run_id)
            return {
                "metrics": run.data.metrics,
                "parameters": run.data.params,
                "version": latest_version.version,
                "stage": latest_version.current_stage
            }
        except Exception as e:
            logger.error(f"Error getting model metrics: {e}")
            return {}


class AnomalyDetectionModel:
    """Anomaly detection model for infrastructure monitoring"""
    
    def __init__(self, model_manager: MLflowModelManager):
        self.model_manager = model_manager
        self.model_name = "aetheredge-anomaly-detection"
        self.experiment_name = "anomaly-detection"
    
    def train_model(self, training_data: pd.DataFrame) -> str:
        """Train anomaly detection model"""
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import classification_report
        
        # Prepare features
        features = training_data.select_dtypes(include=[np.number]).fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        model.fit(X_scaled)
        
        # Generate predictions for evaluation
        predictions = model.predict(X_scaled)
        anomaly_scores = model.decision_function(X_scaled)
        
        # Calculate metrics
        anomaly_rate = (predictions == -1).sum() / len(predictions)
        
        # Log to MLflow
        parameters = {
            "contamination": 0.1,
            "n_estimators": 100,
            "features_count": X_scaled.shape[1],
            "training_samples": X_scaled.shape[0]
        }
        
        metrics = {
            "anomaly_rate": anomaly_rate,
            "mean_anomaly_score": anomaly_scores.mean(),
            "std_anomaly_score": anomaly_scores.std()
        }
        
        # Save preprocessing artifacts
        import joblib
        scaler_path = "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        
        artifacts = {"scaler": scaler_path}
        
        run_id = self.model_manager.log_model(
            model=model,
            model_name=self.model_name,
            experiment_name=self.experiment_name,
            parameters=parameters,
            metrics=metrics,
            artifacts=artifacts,
            model_framework="sklearn"
        )
        
        # Register model
        version = self.model_manager.register_model(self.model_name, run_id)
        
        # Clean up temporary files
        os.remove(scaler_path)
        
        return version
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Predict anomalies in new data"""
        try:
            model = self.model_manager.load_model(self.model_name)
            
            # Prepare features
            features = data.select_dtypes(include=[np.number]).fillna(0)
            
            # Make predictions
            predictions = model.predict(features)
            
            # Calculate anomaly statistics
            anomaly_count = (predictions == -1).sum()
            total_count = len(predictions)
            anomaly_percentage = (anomaly_count / total_count) * 100
            
            return {
                "predictions": predictions.tolist(),
                "anomaly_count": int(anomaly_count),
                "total_count": int(total_count),
                "anomaly_percentage": float(anomaly_percentage),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in anomaly prediction: {e}")
            return {"error": str(e)}


class CostPredictionModel:
    """Cost prediction model for FinOps optimization"""
    
    def __init__(self, model_manager: MLflowModelManager):
        self.model_manager = model_manager
        self.model_name = "aetheredge-cost-prediction"
        self.experiment_name = "cost-prediction"
    
    def train_model(self, training_data: pd.DataFrame, target_column: str) -> str:
        """Train cost prediction model"""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        # Prepare features and target
        feature_columns = [col for col in training_data.columns if col != target_column]
        X = training_data[feature_columns].copy()
        y = training_data[target_column]
        
        # Handle categorical variables
        label_encoders = {}
        for col in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le
        
        # Fill missing values
        X = X.fillna(X.mean())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Log to MLflow
        parameters = {
            "n_estimators": 100,
            "max_depth": 10,
            "features_count": X_train.shape[1],
            "training_samples": X_train.shape[0],
            "target_column": target_column
        }
        
        metrics = {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "r2_score": r2
        }
        
        # Save preprocessing artifacts
        import joblib
        scaler_path = "cost_scaler.pkl"
        encoders_path = "label_encoders.pkl"
        joblib.dump(scaler, scaler_path)
        joblib.dump(label_encoders, encoders_path)
        
        artifacts = {
            "scaler": scaler_path,
            "encoders": encoders_path
        }
        
        run_id = self.model_manager.log_model(
            model=model,
            model_name=self.model_name,
            experiment_name=self.experiment_name,
            parameters=parameters,
            metrics=metrics,
            artifacts=artifacts,
            model_framework="sklearn"
        )
        
        # Register model
        version = self.model_manager.register_model(self.model_name, run_id)
        
        # Clean up temporary files
        os.remove(scaler_path)
        os.remove(encoders_path)
        
        return version
    
    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Predict costs for new data"""
        try:
            model = self.model_manager.load_model(self.model_name)
            
            # Make predictions
            predictions = model.predict(data)
            
            return {
                "predictions": predictions.tolist(),
                "mean_prediction": float(predictions.mean()),
                "total_prediction": float(predictions.sum()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in cost prediction: {e}")
            return {"error": str(e)}


class ModelRetrainingPipeline:
    """Automated model retraining pipeline"""
    
    def __init__(self, model_manager: MLflowModelManager):
        self.model_manager = model_manager
    
    def check_model_drift(self, model_name: str, new_data: pd.DataFrame) -> bool:
        """Check if model needs retraining due to data drift"""
        try:
            # Get current model metrics
            current_metrics = self.model_manager.get_model_metrics(model_name)
            
            # Load current model
            model = self.model_manager.load_model(model_name)
            
            # Make predictions on new data
            features = new_data.select_dtypes(include=[np.number]).fillna(0)
            predictions = model.predict(features)
            
            # Simple drift detection based on prediction distribution
            # In production, use more sophisticated drift detection methods
            mean_prediction = predictions.mean()
            std_prediction = predictions.std()
            
            # Compare with historical metrics (placeholder logic)
            # This should be replaced with proper drift detection algorithms
            drift_threshold = 0.1  # 10% change threshold
            
            # Log drift metrics
            logger.info(f"Model {model_name} - Mean prediction: {mean_prediction}")
            logger.info(f"Model {model_name} - Std prediction: {std_prediction}")
            
            # Return drift status (simplified logic)
            return False  # Placeholder - implement proper drift detection
            
        except Exception as e:
            logger.error(f"Error checking model drift: {e}")
            return False
    
    def schedule_retraining(self, model_name: str, training_data: pd.DataFrame):
        """Schedule model retraining"""
        try:
            logger.info(f"Scheduling retraining for model: {model_name}")
            
            # This would integrate with a job scheduler like Airflow or Kubeflow
            # For now, just log the action
            logger.info(f"Retraining scheduled for {model_name} with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"Error scheduling retraining: {e}")


# MLOps utilities
def setup_mlflow_server():
    """Setup MLflow tracking server"""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    artifact_root = os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlruns")
    
    # Set MLflow configuration
    mlflow.set_tracking_uri(tracking_uri)
    
    return tracking_uri, artifact_root


def initialize_models():
    """Initialize all ML models for AetherEdge"""
    model_manager = MLflowModelManager()
    
    models = {
        "anomaly_detection": AnomalyDetectionModel(model_manager),
        "cost_prediction": CostPredictionModel(model_manager),
        "retraining_pipeline": ModelRetrainingPipeline(model_manager)
    }
    
    return models


if __name__ == "__main__":
    # Example usage
    setup_mlflow_server()
    models = initialize_models()
    
    # Example training data (replace with real data)
    sample_data = pd.DataFrame({
        "cpu_usage": np.random.normal(50, 15, 1000),
        "memory_usage": np.random.normal(60, 20, 1000),
        "network_io": np.random.normal(100, 30, 1000),
        "disk_io": np.random.normal(80, 25, 1000),
        "cost": np.random.normal(100, 25, 1000)
    })
    
    # Train anomaly detection model
    print("Training anomaly detection model...")
    anomaly_version = models["anomaly_detection"].train_model(sample_data)
    print(f"Anomaly detection model version: {anomaly_version}")
    
    # Train cost prediction model
    print("Training cost prediction model...")
    cost_version = models["cost_prediction"].train_model(sample_data, "cost")
    print(f"Cost prediction model version: {cost_version}")
    
    print("MLOps setup completed successfully!")
