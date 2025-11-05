"""
🔥 Shiva Anomaly Detector
========================

AI-powered anomaly detection for predictive healing.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import numpy as np
from dataclasses import dataclass
import json

from ..models.healing import AnomalyReport, AnomalyType

logger = logging.getLogger(__name__)


@dataclass
class AnomalyDetectionResult:
    """Anomaly detection result"""
    is_anomaly: bool
    confidence_score: float
    anomaly_type: str
    severity: str
    baseline_values: Dict[str, float]
    anomaly_values: Dict[str, float]
    threshold_breached: Dict[str, Any]
    recommendations: List[str]


class AnomalyDetector:
    """
    Divine anomaly detection engine
    """

    def __init__(self):
        self.models = {}
        self.thresholds = {}
        self.baseline_cache = {}
        self._initialize_models()
        self._load_thresholds()

    async def analyze_resource(self, resource_id: str, 
                             time_window_hours: int = 24,
                             sensitivity: str = "medium",
                             include_predictions: bool = True) -> List[AnomalyDetectionResult]:
        """
        Analyze resource for anomalies
        """
        try:
            logger.info(f"Analyzing resource {resource_id} for anomalies")
            
            # Get historical data
            metrics_data = await self._get_metrics_data(
                resource_id, time_window_hours
            )
            
            if not metrics_data:
                logger.warning(f"No metrics data found for resource {resource_id}")
                return []
            
            # Analyze each metric
            anomalies = []
            for metric_name, values in metrics_data.items():
                result = await self._analyze_metric(
                    resource_id, metric_name, values, sensitivity
                )
                if result and result.is_anomaly:
                    anomalies.append(result)
            
            # Perform correlation analysis
            if len(anomalies) > 1:
                anomalies = await self._correlate_anomalies(anomalies)
            
            # Add predictions if requested
            if include_predictions:
                predicted_anomalies = await self._predict_future_anomalies(
                    resource_id, metrics_data
                )
                anomalies.extend(predicted_anomalies)
            
            # Store anomaly reports
            for anomaly in anomalies:
                await self._store_anomaly_report(resource_id, anomaly)
            
            logger.info(f"Found {len(anomalies)} anomalies for resource {resource_id}")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error analyzing resource {resource_id}: {str(e)}")
            return []

    async def detect_batch_anomalies(self, resource_ids: List[str],
                                   time_window_hours: int = 24) -> Dict[str, List[AnomalyDetectionResult]]:
        """
        Detect anomalies across multiple resources
        """
        try:
            logger.info(f"Batch anomaly detection for {len(resource_ids)} resources")
            
            results = {}
            
            # Analyze resources in parallel
            tasks = [
                self.analyze_resource(resource_id, time_window_hours)
                for resource_id in resource_ids
            ]
            
            anomaly_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, resource_id in enumerate(resource_ids):
                if isinstance(anomaly_results[i], Exception):
                    logger.error(f"Error analyzing {resource_id}: {anomaly_results[i]}")
                    results[resource_id] = []
                else:
                    results[resource_id] = anomaly_results[i]
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch anomaly detection: {str(e)}")
            return {}

    async def _analyze_metric(self, resource_id: str, metric_name: str,
                            values: List[float], sensitivity: str) -> Optional[AnomalyDetectionResult]:
        """
        Analyze individual metric for anomalies
        """
        try:
            if len(values) < 10:  # Need minimum data points
                return None
            
            # Calculate baseline statistics
            baseline_mean = np.mean(values[:-5])  # Exclude recent values for baseline
            baseline_std = np.std(values[:-5])
            current_values = values[-5:]  # Recent values to check
            
            # Apply sensitivity thresholds
            threshold_multiplier = {
                "low": 3.0,
                "medium": 2.5,
                "high": 2.0
            }.get(sensitivity, 2.5)
            
            upper_threshold = baseline_mean + (threshold_multiplier * baseline_std)
            lower_threshold = baseline_mean - (threshold_multiplier * baseline_std)
            
            # Check for anomalies
            anomalous_values = [
                v for v in current_values 
                if v > upper_threshold or v < lower_threshold
            ]
            
            if not anomalous_values:
                return None
            
            # Calculate confidence score
            max_deviation = max(
                abs(v - baseline_mean) / baseline_std 
                for v in anomalous_values
            )
            confidence_score = min(max_deviation / threshold_multiplier, 1.0)
            
            # Determine anomaly type and severity
            anomaly_type = self._classify_anomaly_type(metric_name, anomalous_values, baseline_mean)
            severity = self._calculate_severity(confidence_score, max_deviation)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                anomaly_type, metric_name, anomalous_values, baseline_mean
            )
            
            return AnomalyDetectionResult(
                is_anomaly=True,
                confidence_score=confidence_score,
                anomaly_type=anomaly_type,
                severity=severity,
                baseline_values={metric_name: baseline_mean},
                anomaly_values={metric_name: max(anomalous_values, key=abs)},
                threshold_breached={
                    "upper": upper_threshold,
                    "lower": lower_threshold,
                    "breached_direction": "upper" if max(anomalous_values) > upper_threshold else "lower"
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing metric {metric_name}: {str(e)}")
            return None

    async def _get_metrics_data(self, resource_id: str, 
                              time_window_hours: int) -> Dict[str, List[float]]:
        """
        Get metrics data for resource
        """
        # Mock implementation - would integrate with monitoring systems
        await asyncio.sleep(0.1)  # Simulate API call
        
        # Generate mock data for demonstration
        import random
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=time_window_hours)
        
        metrics = {
            "cpu_usage": [random.uniform(20, 80) for _ in range(time_window_hours * 6)],
            "memory_usage": [random.uniform(30, 90) for _ in range(time_window_hours * 6)],
            "disk_io": [random.uniform(100, 1000) for _ in range(time_window_hours * 6)],
            "network_io": [random.uniform(50, 500) for _ in range(time_window_hours * 6)],
            "error_rate": [random.uniform(0, 5) for _ in range(time_window_hours * 6)]
        }
        
        # Add some anomalies to the recent data
        if random.random() > 0.7:  # 30% chance of anomaly
            metric_name = random.choice(list(metrics.keys()))
            for i in range(1, 6):  # Last 5 data points
                metrics[metric_name][-i] *= random.uniform(2, 4)  # Spike
        
        return metrics

    def _classify_anomaly_type(self, metric_name: str, anomalous_values: List[float],
                             baseline: float) -> str:
        """
        Classify the type of anomaly based on metric and pattern
        """
        avg_anomaly = np.mean(anomalous_values)
        
        if "cpu" in metric_name.lower():
            return AnomalyType.PERFORMANCE if avg_anomaly > baseline else AnomalyType.CAPACITY
        elif "memory" in metric_name.lower():
            return AnomalyType.CAPACITY
        elif "error" in metric_name.lower():
            return AnomalyType.ERROR_RATE
        elif "latency" in metric_name.lower() or "response" in metric_name.lower():
            return AnomalyType.LATENCY
        else:
            return AnomalyType.RESOURCE_USAGE

    def _calculate_severity(self, confidence_score: float, deviation: float) -> str:
        """
        Calculate anomaly severity based on confidence and deviation
        """
        if confidence_score > 0.8 and deviation > 3.0:
            return "critical"
        elif confidence_score > 0.6 and deviation > 2.0:
            return "high"
        elif confidence_score > 0.4:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, anomaly_type: str, metric_name: str,
                                anomalous_values: List[float], baseline: float) -> List[str]:
        """
        Generate actionable recommendations based on anomaly
        """
        recommendations = []
        avg_anomaly = np.mean(anomalous_values)
        
        if anomaly_type == AnomalyType.PERFORMANCE:
            if avg_anomaly > baseline:
                recommendations.extend([
                    "Consider scaling up resources",
                    "Check for resource-intensive processes",
                    "Review recent configuration changes"
                ])
            else:
                recommendations.extend([
                    "Resources may be underutilized",
                    "Consider scaling down for cost optimization"
                ])
        
        elif anomaly_type == AnomalyType.CAPACITY:
            recommendations.extend([
                "Monitor capacity utilization trends",
                "Implement auto-scaling policies",
                "Review resource allocation strategies"
            ])
        
        elif anomaly_type == AnomalyType.ERROR_RATE:
            recommendations.extend([
                "Investigate application logs",
                "Check dependency health",
                "Review recent deployments"
            ])
        
        return recommendations

    async def _correlate_anomalies(self, anomalies: List[AnomalyDetectionResult]) -> List[AnomalyDetectionResult]:
        """
        Perform correlation analysis between anomalies
        """
        # Simple correlation logic - would be more sophisticated in production
        correlated_anomalies = []
        
        for anomaly in anomalies:
            # Add correlation data
            correlation_info = {
                "correlated_metrics": len(anomalies),
                "correlation_strength": "high" if len(anomalies) > 2 else "medium"
            }
            # In a real implementation, we'd modify the anomaly object
            # to include correlation data
            correlated_anomalies.append(anomaly)
        
        return correlated_anomalies

    async def _predict_future_anomalies(self, resource_id: str,
                                       metrics_data: Dict[str, List[float]]) -> List[AnomalyDetectionResult]:
        """
        Predict future anomalies using trend analysis
        """
        predicted_anomalies = []
        
        # Simple trend prediction - would use ML models in production
        for metric_name, values in metrics_data.items():
            if len(values) < 20:
                continue
            
            # Calculate trend
            recent_trend = np.polyfit(range(len(values[-10:])), values[-10:], 1)[0]
            
            # Predict if trend will cause anomaly
            if abs(recent_trend) > 2.0:  # Significant trend
                predicted_anomalies.append(
                    AnomalyDetectionResult(
                        is_anomaly=True,
                        confidence_score=0.7,
                        anomaly_type="predicted_" + self._classify_anomaly_type(metric_name, values[-5:], np.mean(values)),
                        severity="medium",
                        baseline_values={metric_name: np.mean(values)},
                        anomaly_values={metric_name: values[-1] + (recent_trend * 6)},  # 1 hour prediction
                        threshold_breached={"predicted": True},
                        recommendations=[f"Monitor {metric_name} trend closely", "Consider preventive actions"]
                    )
                )
        
        return predicted_anomalies

    async def _store_anomaly_report(self, resource_id: str, 
                                  anomaly: AnomalyDetectionResult):
        """
        Store anomaly report in database
        """
        try:
            report = AnomalyReport(
                resource_id=resource_id,
                resource_type="auto-detected",
                anomaly_type=anomaly.anomaly_type,
                severity=anomaly.severity,
                confidence_score=anomaly.confidence_score,
                time_window_start=datetime.now(timezone.utc) - timedelta(hours=1),
                time_window_end=datetime.now(timezone.utc),
                baseline_values=anomaly.baseline_values,
                anomaly_values=anomaly.anomaly_values,
                threshold_breached=anomaly.threshold_breached,
                recommended_actions=anomaly.recommendations
            )
            
            await report.save()
            
        except Exception as e:
            logger.error(f"Error storing anomaly report: {str(e)}")

    def _initialize_models(self):
        """Initialize ML models for anomaly detection"""
        # Mock implementation - would load actual ML models
        self.models = {
            "isolation_forest": "Loaded",
            "lstm_autoencoder": "Loaded",
            "statistical_detector": "Loaded"
        }

    def _load_thresholds(self):
        """Load anomaly detection thresholds"""
        self.thresholds = {
            "cpu_usage": {"critical": 90, "high": 80, "medium": 70},
            "memory_usage": {"critical": 95, "high": 85, "medium": 75},
            "error_rate": {"critical": 10, "high": 5, "medium": 2},
            "latency": {"critical": 5000, "high": 2000, "medium": 1000}
        }
