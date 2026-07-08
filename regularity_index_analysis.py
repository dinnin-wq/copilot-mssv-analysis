"""
Regularity Index (Re_g) Analysis Module
Computes Re_g = E² / S for MSSV EEG data

Author: EEG Analysis System
Date: 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy, stats
from scipy.signal import coherence
from typing import Dict, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class RegularityIndexAnalyzer:
    """Compute and analyze regularity index across EEG data"""
    
    def __init__(self, fs: int = 128, epsilon: float = 1e-8):
        """
        Initialize Regularity Index Analyzer
        
        Parameters:
        -----------
        fs : int
            Sampling frequency (Hz)
        epsilon : float
            Small value to avoid division by zero
        """
        self.fs = fs
        self.epsilon = epsilon
    
    def compute_entropy_values(self, data: np.ndarray, 
                               n_bins: int = 50) -> np.ndarray:
        """
        Compute Shannon entropy for each channel
        
        Parameters:
        -----------
        data : ndarray
            EEG data (n_channels x n_samples)
        n_bins : int
            Number of histogram bins
        
        Returns:
        --------
        E_vals : ndarray
            Entropy values per channel (n_channels,)
        """
        n_channels = data.shape[0]
        E_vals = np.zeros(n_channels)
        
        for ch in range(n_channels):
            hist, _ = np.histogram(data[ch, :], bins=n_bins, density=True)
            hist = hist + 1e-10
            E_vals[ch] = entropy(hist)
        
        return E_vals
    
    def compute_connectivity_values(self, data: np.ndarray) -> np.ndarray:
        """
        Compute mean coherence for each channel pair
        
        Parameters:
        -----------
        data : ndarray
            EEG data (n_channels x n_samples)
        
        Returns:
        --------
        S_vals : ndarray
            Mean coherence values per channel (n_channels,)
            (computed as mean coherence with all other channels)
        """
        n_channels = data.shape[0]
        S_vals = np.zeros(n_channels)
        
        for i in range(n_channels):
            coherences = []
            for j in range(n_channels):
                if i != j:
                    _, Cxy = coherence(data[i], data[j], fs=self.fs)
                    coherences.append(np.mean(Cxy))
            
            S_vals[i] = np.mean(coherences) if coherences else 0.0
        
        return S_vals
    
    def compute_regularity_index(self, E_vals: np.ndarray, 
                                 S_vals: np.ndarray) -> np.ndarray:
        """
        Compute regularity index: Re_g = E² / S
        
        Parameters:
        -----------
        E_vals : ndarray
            Entropy values (n_channels,)
        S_vals : ndarray
            Connectivity values (n_channels,)
        
        Returns:
        --------
        Re_g_vals : ndarray
            Regularity index values (n_channels,)
        """
        Re_g_vals = (E_vals ** 2) / (S_vals + self.epsilon)
        return Re_g_vals
    
    def compute_global_metrics(self, data: np.ndarray) -> Dict:
        """
        Compute global metrics (single values across all channels)
        
        Parameters:
        -----------
        data : ndarray
            EEG data (n_channels x n_samples)
        
        Returns:
        --------
        metrics : dict
            Global E, S, and Re_g values
        """
        # Global entropy (from all data)
        hist, _ = np.histogram(data.flatten(), bins=50, density=True)
        hist = hist + 1e-10
        E_global = entropy(hist)
        
        # Global connectivity (mean across all pairs)
        n_channels = data.shape[0]
        coherences = []
        for i in range(n_channels):
            for j in range(i+1, n_channels):
                _, Cxy = coherence(data[i], data[j], fs=self.fs)
                coherences.append(np.mean(Cxy))
        
        S_global = np.mean(coherences) if coherences else 0.0
        Re_g_global = (E_global ** 2) / (S_global + self.epsilon)
        
        return {
            'entropy_global': E_global,
            'connectivity_global': S_global,
            'regularity_index_global': Re_g_global
        }
    
    def compute_all_metrics(self, data: np.ndarray) -> Dict:
        """
        Compute all regularity metrics
        
        Parameters:
        -----------
        data : ndarray
            EEG data (n_channels x n_samples)
        
        Returns:
        --------
        metrics : dict
            All computed metrics
        """
        # Per-channel metrics
        E_vals = self.compute_entropy_values(data)
        S_vals = self.compute_connectivity_values(data)
        Re_g_vals = self.compute_regularity_index(E_vals, S_vals)
        
        # Global metrics
        global_metrics = self.compute_global_metrics(data)
        
        return {
            'entropy_per_channel': E_vals,
            'connectivity_per_channel': S_vals,
            'regularity_index_per_channel': Re_g_vals,
            'entropy_global': global_metrics['entropy_global'],
            'connectivity_global': global_metrics['connectivity_global'],
            'regularity_index_global': global_metrics['regularity_index_global'],
            'mean_regularity_index': np.mean(Re_g_vals),
            'std_regularity_index': np.std(Re_g_vals),
            'min_regularity_index': np.min(Re_g_vals),
            'max_regularity_index': np.max(Re_g_vals)
        }
    
    def classify_sleep_state_per_channel(self, Re_g_vals: np.ndarray, 
                                         E_vals: np.ndarray) -> List[Tuple[str, float]]:
        """
        Classify sleep state for each channel
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values (n_channels,)
        E_vals : ndarray
            Entropy values (n_channels,)
        
        Returns:
        --------
        classifications : list
            List of (sleep_state, confidence) tuples per channel
        """
        classifications = []
        
        for ch in range(len(Re_g_vals)):
            re_g = Re_g_vals[ch]
            e = E_vals[ch]
            
            if re_g > 2.0 and e > 2.5:
                state = "Wake/REM"
                conf = 0.7
            elif 1.0 < re_g <= 2.0 and 2.0 < e <= 2.5:
                state = "Light Sleep (N1/N2)"
                conf = 0.75
            elif re_g <= 1.0 and e <= 2.0:
                state = "Deep Sleep (N3)"
                conf = 0.8
            else:
                state = "Undetermined"
                conf = 0.5
            
            classifications.append((state, conf))
        
        return classifications
    
    def classify_sleep_state_global(self, Re_g: float, 
                                    E: float, S: float) -> Tuple[str, float]:
        """
        Classify overall sleep state from global metrics
        
        Parameters:
        -----------
        Re_g : float
            Global regularity index
        E : float
            Global entropy
        S : float
            Global connectivity
        
        Returns:
        --------
        sleep_state : str
            Predicted sleep state
        confidence : float
            Confidence score (0-1)
        """
        if Re_g > 2.0 and E > 2.5:
            return "Wake/REM", 0.7
        elif 1.0 < Re_g <= 2.0 and 2.0 < E <= 2.5:
            return "Light Sleep (N1/N2)", 0.75
        elif Re_g <= 1.0 and E <= 2.0:
            return "Deep Sleep (N3)", 0.8
        else:
            return "Undetermined", 0.5
    
    def compute_time_windowed_reg(self, data: np.ndarray,
                                  window_sec: float = 4.0,
                                  overlap: float = 0.5) -> pd.DataFrame:
        """
        Compute regularity index over time windows
        
        Parameters:
        -----------
        data : ndarray
            EEG data (n_channels x n_samples)
        window_sec : float
            Window length in seconds
        overlap : float
            Overlap ratio (0-1)
        
        Returns:
        --------
        results : DataFrame
            Time-windowed regularity metrics
        """
        window_samples = int(window_sec * self.fs)
        step_samples = int(window_samples * (1 - overlap))
        
        results = []
        window_idx = 0
        
        for start in range(0, data.shape[1] - window_samples, step_samples):
            end = start + window_samples
            window_data = data[:, start:end]
            
            metrics = self.compute_all_metrics(window_data)
            
            results.append({
                'window': window_idx,
                'time_sec': start / self.fs,
                'entropy_global': metrics['entropy_global'],
                'connectivity_global': metrics['connectivity_global'],
                'regularity_index_global': metrics['regularity_index_global'],
                'mean_re_g': metrics['mean_regularity_index']
            })
            
            window_idx += 1
        
        return pd.DataFrame(results)
    
    def visualize_regularity_index(self, Re_g_vals: np.ndarray,
                                   E_vals: np.ndarray,
                                   S_vals: np.ndarray,
                                   channel_names: Optional[List[str]] = None):
        """
        Visualize regularity index metrics
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values per channel
        E_vals : ndarray
            Entropy values per channel
        S_vals : ndarray
            Connectivity values per channel
        channel_names : list, optional
            Channel names for labels
        """
        n_channels = len(Re_g_vals)
        if channel_names is None:
            channel_names = [f'Ch {i}' for i in range(n_channels)]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot 1: Regularity Index per channel
        ax = axes[0, 0]
        ax.bar(channel_names, Re_g_vals, color='steelblue')
        ax.set_ylabel('Regularity Index (Re_g)')
        ax.set_title('Regularity Index per Channel')
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 2: Entropy per channel
        ax = axes[0, 1]
        ax.bar(channel_names, E_vals, color='coral')
        ax.set_ylabel('Entropy (E)')
        ax.set_title('Entropy per Channel')
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 3: Connectivity per channel
        ax = axes[1, 0]
        ax.bar(channel_names, S_vals, color='lightgreen')
        ax.set_ylabel('Connectivity (S)')
        ax.set_title('Connectivity per Channel')
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Plot 4: E vs S scatter (colored by Re_g)
        ax = axes[1, 1]
        scatter = ax.scatter(S_vals, E_vals, c=Re_g_vals, s=200, 
                            cmap='viridis', edgecolors='black', linewidth=2)
        ax.set_xlabel('Connectivity (S)')
        ax.set_ylabel('Entropy (E)')
        ax.set_title('Entropy vs Connectivity (colored by Re_g)')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Re_g')
        ax.grid(True, alpha=0.3)
        
        # Add labels to points
        for i, name in enumerate(channel_names):
            ax.annotate(name, (S_vals[i], E_vals[i]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        return fig
    
    def compute_statistics(self, Re_g_vals: np.ndarray) -> Dict:
        """
        Compute statistical summary of regularity index
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values
        
        Returns:
        --------
        stats : dict
            Statistical summary
        """
        return {
            'mean': np.mean(Re_g_vals),
            'median': np.median(Re_g_vals),
            'std': np.std(Re_g_vals),
            'min': np.min(Re_g_vals),
            'max': np.max(Re_g_vals),
            'q25': np.percentile(Re_g_vals, 25),
            'q75': np.percentile(Re_g_vals, 75),
            'skewness': stats.skew(Re_g_vals),
            'kurtosis': stats.kurtosis(Re_g_vals)
        }


# ============== EXAMPLE USAGE ==============

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("REGULARITY INDEX (Re_g) ANALYSIS")
    print("="*80)
    
    # Simulate multi-channel EEG data
    n_channels = 4
    duration_sec = 30
    fs = 128
    n_samples = duration_sec * fs
    
    data = np.random.randn(n_channels, n_samples) * 100
    
    # Initialize analyzer
    analyzer = RegularityIndexAnalyzer(fs=fs)
    
    print("\n[1] Computing Regularity Index Metrics")
    print("-" * 80)
    
    # Per-channel metrics
    E_vals = analyzer.compute_entropy_values(data)
    S_vals = analyzer.compute_connectivity_values(data)
    Re_g_vals = analyzer.compute_regularity_index(E_vals, S_vals)
    
    print(f"\nPer-Channel Metrics:")
    for ch in range(n_channels):
        print(f"  Channel {ch}: E={E_vals[ch]:.4f}, S={S_vals[ch]:.4f}, Re_g={Re_g_vals[ch]:.4f}")
    
    # Global metrics
    print("\n[2] Computing Global Metrics")
    print("-" * 80)
    
    global_metrics = analyzer.compute_all_metrics(data)
    
    print(f"Global Entropy (E): {global_metrics['entropy_global']:.4f}")
    print(f"Global Connectivity (S): {global_metrics['connectivity_global']:.4f}")
    print(f"Global Regularity Index (Re_g): {global_metrics['regularity_index_global']:.4f}")
    
    # Sleep state classification
    print("\n[3] Sleep State Classification")
    print("-" * 80)
    
    sleep_states = analyzer.classify_sleep_state_per_channel(Re_g_vals, E_vals)
    for ch, (state, conf) in enumerate(sleep_states):
        print(f"  Channel {ch}: {state} (confidence: {conf:.2%})")
    
    global_state, global_conf = analyzer.classify_sleep_state_global(
        global_metrics['regularity_index_global'],
        global_metrics['entropy_global'],
        global_metrics['connectivity_global']
    )
    print(f"\nGlobal Sleep State: {global_state} (confidence: {global_conf:.2%})")
    
    # Statistics
    print("\n[4] Regularity Index Statistics")
    print("-" * 80)
    
    reg_stats = analyzer.compute_statistics(Re_g_vals)
    for key, value in reg_stats.items():
        print(f"  {key.capitalize()}: {value:.4f}")
    
    # Time-windowed analysis
    print("\n[5] Time-Windowed Regularity Index")
    print("-" * 80)
    
    windowed = analyzer.compute_time_windowed_reg(data, window_sec=4.0)
    print(windowed.head(10))
    
    # Visualization
    print("\n[6] Generating Visualization")
    print("-" * 80)
    
    fig = analyzer.visualize_regularity_index(Re_g_vals, E_vals, S_vals)
    plt.savefig('regularity_index_analysis.png', dpi=150, bbox_inches='tight')
    print("✓ Visualization saved: regularity_index_analysis.png")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE ✓")
    print("="*80)
