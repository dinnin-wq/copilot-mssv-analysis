"""
Mouse Sleep Staging Validation (MSSV) EEG Analysis Pipeline
Complete analysis of all 92 mice with M365 Copilot integration

Author: EEG Analysis System
Date: 2025
License: CC0
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from scipy.stats import entropy
from scipy.signal import coherence, welch, hilbert
import mne
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EEGMetrics:
    """Container for EEG analysis metrics"""
    subject_id: str
    file_path: str
    entropy: float
    connectivity: float
    regularity_index: float
    approx_entropy: float
    sample_entropy: float
    mean_amplitude: float
    std_amplitude: float
    predicted_sleep_state: str
    confidence: float
    spectral_metrics: Dict
    channel_metrics: List[Dict]
    timestamp: str


class MSSVEEGAnalyzer:
    """Main analyzer for MSSV dataset"""
    
    def __init__(self, dataset_root: str = "/data/OpenNeuroDatasets/ds006366", 
                 fs: int = 128):
        """
        Initialize MSSV EEG Analyzer
        
        Parameters:
        -----------
        dataset_root : str
            Root path of MSSV dataset
        fs : int
            Sampling frequency (128 Hz for MSSV)
        """
        self.dataset_root = Path(dataset_root)
        self.fs = fs
        self.results = []
        
    def get_subject_list(self) -> List[str]:
        """Get all subject IDs from dataset"""
        subjects = []
        for sub_dir in self.dataset_root.glob('sub-*'):
            if sub_dir.is_dir():
                subjects.append(sub_dir.name)
        return sorted(subjects)
    
    def get_eeg_files(self, subject_id: str) -> List[Path]:
        """Get EEG .edf files for a subject"""
        subject_path = self.dataset_root / subject_id / 'eeg'
        if subject_path.exists():
            return sorted(subject_path.glob('*_eeg.edf'))
        return []
    
    def load_edf_file(self, filepath: str) -> Optional[np.ndarray]:
        """
        Load EDF file safely
        
        Parameters:
        -----------
        filepath : str
            Path to EDF file
        
        Returns:
        --------
        data : ndarray or None
            EEG data (n_channels x n_samples) or None if load fails
        """
        try:
            raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
            data = raw.get_data()
            logger.info(f"Loaded {filepath}: shape {data.shape}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {str(e)}")
            return None
    
    def calculate_entropy(self, data: np.ndarray, bins: int = 50) -> float:
        """Calculate Shannon entropy"""
        hist, _ = np.histogram(data.flatten(), bins=bins, density=True)
        hist = hist + 1e-10
        return entropy(hist)
    
    def compute_connectivity(self, data: np.ndarray) -> float:
        """Compute mean coherence across all channel pairs"""
        n_channels = data.shape[0]
        connectivity_values = []
        
        for i in range(n_channels):
            for j in range(i+1, n_channels):
                _, Cxy = coherence(data[i], data[j], fs=self.fs)
                connectivity_values.append(np.mean(Cxy))
        
        return np.mean(connectivity_values) if connectivity_values else 0.0
    
    def compute_regularity_index(self, E: float, S: float, epsilon: float = 1e-8) -> float:
        """Compute regularity index (Re_g)"""
        return (E ** 2) / (S + epsilon)
    
    def compute_approx_entropy(self, data: np.ndarray, m: int = 2, r: Optional[float] = None) -> float:
        """Compute approximate entropy"""
        if r is None:
            r = 0.2 * np.std(data)
        
        N = len(data)
        count = []
        
        for k in [m, m+1]:
            count_k = 0
            for i in range(N - k + 1):
                for j in range(i+1, N - k + 1):
                    if np.linalg.norm(data[i:i+k] - data[j:j+k], ord=np.inf) < r:
                        count_k += 1
            count.append(count_k)
        
        if count[1] == 0:
            return 0.0
        
        return -np.log(count[1] / count[0]) if count[0] > 0 else 0.0
    
    def compute_sample_entropy(self, data: np.ndarray, m: int = 2, r: Optional[float] = None) -> float:
        """Compute sample entropy"""
        if r is None:
            r = 0.2 * np.std(data)
        
        N = len(data)
        templates_m = [data[i:i+m] for i in range(N - m + 1)]
        templates_m1 = [data[i:i+m+1] for i in range(N - m)]
        
        count_m = sum([sum([np.linalg.norm(templates_m[i] - templates_m[j], ord=np.inf) < r 
                           for j in range(i+1, len(templates_m))]) for i in range(len(templates_m))])
        count_m1 = sum([sum([np.linalg.norm(templates_m1[i] - templates_m1[j], ord=np.inf) < r 
                            for j in range(i+1, len(templates_m1))]) for i in range(len(templates_m1))])
        
        if count_m == 0:
            return 0.0
        
        return -np.log(count_m1 / count_m) if count_m1 > 0 else 0.0
    
    def compute_spectral_metrics(self, data: np.ndarray, 
                                freq_bands: Optional[Dict] = None) -> Dict:
        """Compute spectral metrics by frequency band"""
        if freq_bands is None:
            freq_bands = {
                'delta': (0.5, 4),
                'theta': (4, 8),
                'alpha': (8, 12),
                'beta': (12, 30),
                'gamma': (30, 50)
            }
        
        spectral_metrics = {}
        
        for band_name, (freq_low, freq_high) in freq_bands.items():
            band_values = []
            
            for ch in range(data.shape[0]):
                f, pxx = welch(data[ch], fs=self.fs, nperseg=256)
                band_idx = (f >= freq_low) & (f <= freq_high)
                
                if np.any(band_idx):
                    band_power = pxx[band_idx]
                    band_power_norm = band_power / np.sum(pxx) + 1e-10
                    band_entropy = entropy(band_power_norm)
                    band_values.append(band_entropy)
            
            if band_values:
                mean_entropy = np.mean(band_values)
                re_g_band = (mean_entropy ** 2) / (np.std(band_values) + 1e-8)
                spectral_metrics[band_name] = {
                    'entropy': float(mean_entropy),
                    'regularity_index': float(re_g_band),
                    'std_entropy': float(np.std(band_values))
                }
        
        return spectral_metrics
    
    def compute_channel_metrics(self, data: np.ndarray) -> List[Dict]:
        """Compute metrics per channel"""
        channel_metrics = []
        
        for ch in range(data.shape[0]):
            channel_data = data[ch, :]
            
            hist, _ = np.histogram(channel_data, bins=50, density=True)
            hist = hist + 1e-10
            ch_entropy = entropy(hist)
            
            variance = np.var(channel_data)
            mean_amp = np.mean(np.abs(channel_data))
            
            channel_metrics.append({
                'channel': int(ch),
                'entropy': float(ch_entropy),
                'variance': float(variance),
                'mean_amplitude': float(mean_amp),
                'std_amplitude': float(np.std(channel_data))
            })
        
        return channel_metrics
    
    def classify_sleep_state(self, Re_g: float, E: float, S: float) -> Tuple[str, float]:
        """
        Classify sleep state based on metrics
        
        Returns:
        --------
        sleep_state : str
            Predicted sleep state
        confidence : float
            Confidence score (0-1)
        """
        if Re_g > 2.0 and E > 2.5:
            sleep_state = "Wake/REM"
            confidence = 0.7
        elif 1.0 < Re_g <= 2.0 and 2.0 < E <= 2.5:
            sleep_state = "Light Sleep (N1/N2)"
            confidence = 0.75
        elif Re_g <= 1.0 and E <= 2.0:
            sleep_state = "Deep Sleep (N3)"
            confidence = 0.8
        else:
            sleep_state = "Undetermined"
            confidence = 0.5
        
        return sleep_state, confidence
    
    def analyze_subject(self, subject_id: str) -> Optional[EEGMetrics]:
        """
        Analyze a single subject's EEG data
        
        Parameters:
        -----------
        subject_id : str
            Subject identifier (e.g., 'sub-001')
        
        Returns:
        --------
        metrics : EEGMetrics or None
            Analysis metrics or None if analysis fails
        """
        logger.info(f"Analyzing {subject_id}...")
        
        eeg_files = self.get_eeg_files(subject_id)
        if not eeg_files:
            logger.warning(f"No EEG files found for {subject_id}")
            return None
        
        # Use first EEG file
        eeg_file = eeg_files[0]
        data = self.load_edf_file(str(eeg_file))
        
        if data is None:
            return None
        
        # Calculate metrics
        E = self.calculate_entropy(data)
        S = self.compute_connectivity(data)
        Re_g = self.compute_regularity_index(E, S)
        
        # Complex metrics (on flattened data to speed up)
        flat_data = data.flatten()
        approx_ent = self.compute_approx_entropy(flat_data)
        sample_ent = self.compute_sample_entropy(flat_data)
        
        # Spectral and channel metrics
        spectral = self.compute_spectral_metrics(data)
        channel_metrics = self.compute_channel_metrics(data)
        
        # Sleep state classification
        sleep_state, confidence = self.classify_sleep_state(Re_g, E, S)
        
        # Create metrics object
        metrics = EEGMetrics(
            subject_id=subject_id,
            file_path=str(eeg_file),
            entropy=float(E),
            connectivity=float(S),
            regularity_index=float(Re_g),
            approx_entropy=float(approx_ent),
            sample_entropy=float(sample_ent),
            mean_amplitude=float(np.mean(np.abs(data))),
            std_amplitude=float(np.std(data)),
            predicted_sleep_state=sleep_state,
            confidence=float(confidence),
            spectral_metrics=spectral,
            channel_metrics=channel_metrics,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✓ {subject_id}: Re_g={Re_g:.4f}, Sleep State={sleep_state}")
        return metrics
    
    def analyze_all_subjects(self, max_subjects: Optional[int] = None) -> List[EEGMetrics]:
        """
        Analyze all subjects in dataset
        
        Parameters:
        -----------
        max_subjects : int or None
            Limit analysis to first N subjects (None = all)
        
        Returns:
        --------
        results : list
            List of EEGMetrics objects
        """
        subjects = self.get_subject_list()
        
        if max_subjects:
            subjects = subjects[:max_subjects]
        
        logger.info(f"Starting analysis of {len(subjects)} subjects...")
        
        results = []
        for subject_id in subjects:
            metrics = self.analyze_subject(subject_id)
            if metrics:
                results.append(metrics)
                self.results.append(metrics)
        
        logger.info(f"Analysis complete: {len(results)}/{len(subjects)} subjects")
        return results
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export results to pandas DataFrame"""
        data_dicts = [asdict(m) for m in self.results]
        
        # Flatten nested dicts
        flattened = []
        for d in data_dicts:
            flat = {
                'subject_id': d['subject_id'],
                'entropy': d['entropy'],
                'connectivity': d['connectivity'],
                'regularity_index': d['regularity_index'],
                'approx_entropy': d['approx_entropy'],
                'sample_entropy': d['sample_entropy'],
                'mean_amplitude': d['mean_amplitude'],
                'std_amplitude': d['std_amplitude'],
                'predicted_sleep_state': d['predicted_sleep_state'],
                'confidence': d['confidence'],
                'n_channels': len(d['channel_metrics'])
            }
            flattened.append(flat)
        
        return pd.DataFrame(flattened)
    
    def export_to_json(self, output_file: str = 'mssv_analysis_results.json'):
        """Export results to JSON"""
        data = {
            'metadata': {
                'dataset': 'MSSV (ds006366)',
                'analysis_date': datetime.now().isoformat(),
                'n_subjects': len(self.results),
                'sampling_rate': self.fs,
                'version': '1.0'
            },
            'results': [asdict(m) for m in self.results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Results exported to {output_file}")
        return output_file
    
    def generate_summary_statistics(self) -> Dict:
        """Generate summary statistics"""
        if not self.results:
            return {}
        
        df = self.export_to_dataframe()
        
        summary = {
            'total_subjects': len(self.results),
            'entropy': {
                'mean': float(df['entropy'].mean()),
                'std': float(df['entropy'].std()),
                'min': float(df['entropy'].min()),
                'max': float(df['entropy'].max())
            },
            'connectivity': {
                'mean': float(df['connectivity'].mean()),
                'std': float(df['connectivity'].std()),
                'min': float(df['connectivity'].min()),
                'max': float(df['connectivity'].max())
            },
            'regularity_index': {
                'mean': float(df['regularity_index'].mean()),
                'std': float(df['regularity_index'].std()),
                'min': float(df['regularity_index'].min()),
                'max': float(df['regularity_index'].max())
            },
            'sleep_state_distribution': df['predicted_sleep_state'].value_counts().to_dict(),
            'mean_confidence': float(df['confidence'].mean())
        }
        
        return summary


class M365CopilotConnector:
    """Connector for M365 Copilot integration"""
    
    def __init__(self, tenant_id: str = None, client_id: str = None, 
                 client_secret: str = None):
        """
        Initialize M365 Copilot Connector
        
        Parameters:
        -----------
        tenant_id : str
            Azure AD tenant ID
        client_id : str
            Application (client) ID
        client_secret : str
            Client secret for authentication
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Azure AD
        
        Returns:
        --------
        success : bool
            True if authentication successful
        """
        try:
            import requests
            
            url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default'
            }
            
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                logger.info("✓ Successfully authenticated with M365")
                return True
            else:
                logger.error(f"Authentication failed: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def create_copilot_grounding(self, analysis_results: Dict) -> Dict:
        """
        Create grounding data for M365 Copilot
        
        Parameters:
        -----------
        analysis_results : dict
            Analysis results from MSSV analyzer
        
        Returns:
        --------
        grounding : dict
            Formatted data for Copilot grounding
        """
        grounding = {
            'dataset_name': 'Mouse Sleep Staging Validation (MSSV)',
            'dataset_id': 'ds006366',
            'dataset_url': 'https://openneuro.org/datasets/ds006366',
            'analysis_type': 'EEG Signal Analysis',
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'entropy_analysis': {
                    'description': 'Shannon entropy measuring signal complexity',
                    'interpretation': 'Higher entropy indicates more complex/random signal'
                },
                'connectivity_analysis': {
                    'description': 'Mean coherence between EEG channel pairs',
                    'interpretation': 'Higher connectivity indicates more synchronized channels'
                },
                'regularity_index': {
                    'description': 'Ratio of entropy squared to connectivity',
                    'formula': 'Re_g = E² / (S + ε)',
                    'interpretation': 'Distinguishes sleep states: High=Wake/REM, Low=Deep Sleep'
                }
            },
            'summary_statistics': analysis_results,
            'data_sources': [
                {
                    'name': 'MSSV Dataset',
                    'subjects': 92,
                    'channels_per_subject': 'Variable',
                    'sampling_rate': '128 Hz',
                    'format': 'EDF'
                }
            ]
        }
        
        return grounding
    
    def upload_to_copilot(self, grounding: Dict, 
                         knowledge_base_id: str = None) -> bool:
        """
        Upload grounding data to Copilot knowledge base
        
        Parameters:
        -----------
        grounding : dict
            Grounding data
        knowledge_base_id : str
            Target knowledge base ID
        
        Returns:
        --------
        success : bool
            True if upload successful
        """
        try:
            import requests
            
            if not self.access_token:
                logger.error("Not authenticated. Call authenticate() first.")
                return False
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Example: Graph API endpoint for Copilot
            url = f"https://graph.microsoft.com/v1.0/me/copilot/groundingData"
            
            response = requests.post(url, json=grounding, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info("✓ Successfully uploaded to M365 Copilot")
                return True
            else:
                logger.error(f"Upload failed: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return False


if __name__ == "__main__":
    print("="*80)
    print("MSSV EEG ANALYSIS PIPELINE WITH M365 COPILOT INTEGRATION")
    print("="*80)
    
    analyzer = MSSVEEGAnalyzer(
        dataset_root="/data/OpenNeuroDatasets/ds006366",
        fs=128
    )
    
    results = analyzer.analyze_all_subjects(max_subjects=5)
    summary = analyzer.generate_summary_statistics()
    
    print(json.dumps(summary, indent=2))
