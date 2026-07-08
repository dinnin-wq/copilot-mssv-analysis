"""
Regularity Index Visualization Module
Comprehensive plotting functions for Re_g analysis

Author: EEG Analysis System
Date: 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from typing import List, Optional, Tuple, Dict
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11


class RegularityIndexVisualizer:
    """Comprehensive visualization for regularity index analysis"""
    
    def __init__(self):
        """Initialize visualizer"""
        self.colors = {
            'wake_rem': '#FF6B6B',      # Red
            'light_sleep': '#FFD93D',    # Yellow
            'deep_sleep': '#6BCB77',     # Green
            'undetermined': '#A8A8A8'    # Gray
        }
    
    def plot_re_g_with_threshold(self, Re_g_vals: np.ndarray,
                                  channel_names: Optional[List[str]] = None,
                                  title: str = "Regularity Index (Re_g) Analysis",
                                  figsize: Tuple = (14, 6)):
        """
        Plot Re_g values with sleep state threshold lines
        
        Implements:
        plt.plot(Re_g_vals)
        plt.axhline(1.0)
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values
        channel_names : list, optional
            Channel names for x-axis labels
        title : str
            Plot title
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        n_channels = len(Re_g_vals)
        if channel_names is None:
            channel_names = [f'Ch {i}' for i in range(n_channels)]
        
        # Main plot
        x_vals = np.arange(n_channels)
        ax.plot(x_vals, Re_g_vals, 'o-', linewidth=2.5, markersize=10, 
               color='steelblue', label='Re_g values')
        
        # Threshold lines (sleep state boundaries)
        ax.axhline(1.0, color='green', linestyle='--', linewidth=2.5, 
                  label='Deep Sleep threshold (Re_g=1.0)')
        ax.axhline(2.0, color='orange', linestyle='--', linewidth=2.5,
                  label='Light Sleep threshold (Re_g=2.0)')
        ax.axhline(2.5, color='red', linestyle='--', linewidth=2.5,
                  label='Wake/REM threshold (Re_g=2.5)')
        
        # Background regions
        ax.axhspan(0, 1.0, alpha=0.1, color='green', label='Deep Sleep (Re_g < 1.0)')
        ax.axhspan(1.0, 2.0, alpha=0.1, color='yellow', label='Light Sleep (1.0 < Re_g < 2.0)')
        ax.axhspan(2.0, ax.get_ylim()[1], alpha=0.1, color='red', label='Wake/REM (Re_g > 2.0)')
        
        # Labels and formatting
        ax.set_xticks(x_vals)
        ax.set_xticklabels(channel_names, rotation=45, ha='right')
        ax.set_xlabel('Channel', fontsize=12, fontweight='bold')
        ax.set_ylabel('Regularity Index (Re_g)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(loc='upper right', fontsize=10)
        
        # Add value labels on points
        for i, val in enumerate(Re_g_vals):
            ax.text(i, val + 0.15, f'{val:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def plot_re_g_distribution(self, Re_g_vals: np.ndarray,
                              title: str = "Regularity Index Distribution",
                              figsize: Tuple = (12, 6)):
        """
        Plot histogram and KDE of Re_g values
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values
        title : str
            Plot title
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Histogram
        ax.hist(Re_g_vals, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        
        # KDE
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(Re_g_vals)
        x_range = np.linspace(Re_g_vals.min(), Re_g_vals.max(), 100)
        ax.plot(x_range, kde(x_range) * len(Re_g_vals) * (Re_g_vals.max() - Re_g_vals.min()) / 20,
               'r-', linewidth=2, label='KDE')
        
        # Thresholds
        ax.axvline(1.0, color='green', linestyle='--', linewidth=2, label='Deep Sleep')
        ax.axvline(2.0, color='orange', linestyle='--', linewidth=2, label='Light Sleep')
        
        # Statistics
        mean_val = np.mean(Re_g_vals)
        median_val = np.median(Re_g_vals)
        ax.axvline(mean_val, color='purple', linestyle=':', linewidth=2, label=f'Mean={mean_val:.2f}')
        ax.axvline(median_val, color='brown', linestyle=':', linewidth=2, label=f'Median={median_val:.2f}')
        
        ax.set_xlabel('Regularity Index (Re_g)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig
    
    def plot_re_g_vs_entropy_connectivity(self, Re_g_vals: np.ndarray,
                                         E_vals: np.ndarray,
                                         S_vals: np.ndarray,
                                         channel_names: Optional[List[str]] = None,
                                         figsize: Tuple = (14, 6)):
        """
        Plot Re_g with constituent entropy and connectivity
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values
        E_vals : ndarray
            Entropy values
        S_vals : ndarray
            Connectivity values
        channel_names : list, optional
            Channel names
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        n_channels = len(Re_g_vals)
        if channel_names is None:
            channel_names = [f'Ch {i}' for i in range(n_channels)]
        
        x_vals = np.arange(n_channels)
        
        # Plot 1: Entropy
        axes[0].bar(x_vals, E_vals, color='coral', alpha=0.7, edgecolor='black')
        axes[0].set_ylabel('Entropy (E)', fontsize=11, fontweight='bold')
        axes[0].set_title('Shannon Entropy per Channel', fontsize=12, fontweight='bold')
        axes[0].set_xticks(x_vals)
        axes[0].set_xticklabels(channel_names, rotation=45, ha='right')
        axes[0].grid(True, alpha=0.3, axis='y')
        axes[0].axhline(2.0, color='red', linestyle='--', alpha=0.5)
        axes[0].axhline(2.5, color='orange', linestyle='--', alpha=0.5)
        
        # Plot 2: Connectivity
        axes[1].bar(x_vals, S_vals, color='lightgreen', alpha=0.7, edgecolor='black')
        axes[1].set_ylabel('Connectivity (S)', fontsize=11, fontweight='bold')
        axes[1].set_title('Mean Coherence per Channel', fontsize=12, fontweight='bold')
        axes[1].set_xticks(x_vals)
        axes[1].set_xticklabels(channel_names, rotation=45, ha='right')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # Plot 3: Regularity Index
        bars = axes[2].bar(x_vals, Re_g_vals, edgecolor='black')
        
        # Color bars by sleep state
        for i, (bar, val) in enumerate(zip(bars, Re_g_vals)):
            if val > 2.0:
                bar.set_color(self.colors['wake_rem'])
            elif val > 1.0:
                bar.set_color(self.colors['light_sleep'])
            else:
                bar.set_color(self.colors['deep_sleep'])
        
        axes[2].set_ylabel('Regularity Index (Re_g)', fontsize=11, fontweight='bold')
        axes[2].set_title('Re_g = E² / S per Channel', fontsize=12, fontweight='bold')
        axes[2].set_xticks(x_vals)
        axes[2].set_xticklabels(channel_names, rotation=45, ha='right')
        axes[2].axhline(1.0, color='green', linestyle='--', linewidth=2)
        axes[2].axhline(2.0, color='orange', linestyle='--', linewidth=2)
        axes[2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig
    
    def plot_re_g_time_series(self, time_sec: np.ndarray,
                             Re_g_time: np.ndarray,
                             title: str = "Regularity Index Over Time",
                             figsize: Tuple = (14, 6)):
        """
        Plot Re_g as time series
        
        Parameters:
        -----------
        time_sec : ndarray
            Time values in seconds
        Re_g_time : ndarray
            Regularity index values over time
        title : str
            Plot title
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Main line
        ax.plot(time_sec, Re_g_time, linewidth=2.5, color='steelblue', label='Re_g')
        
        # Fill between thresholds
        ax.fill_between(time_sec, 0, 1.0, alpha=0.1, color='green', label='Deep Sleep')
        ax.fill_between(time_sec, 1.0, 2.0, alpha=0.1, color='yellow', label='Light Sleep')
        ax.fill_between(time_sec, 2.0, ax.get_ylim()[1], alpha=0.1, color='red', label='Wake/REM')
        
        # Threshold lines
        ax.axhline(1.0, color='green', linestyle='--', linewidth=2, alpha=0.7)
        ax.axhline(2.0, color='orange', linestyle='--', linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Regularity Index (Re_g)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def plot_re_g_sleep_state_regions(self, Re_g_vals: np.ndarray,
                                     E_vals: np.ndarray,
                                     channel_names: Optional[List[str]] = None,
                                     figsize: Tuple = (14, 7)):
        """
        Plot Re_g with sleep state regions highlighted
        
        Parameters:
        -----------
        Re_g_vals : ndarray
            Regularity index values
        E_vals : ndarray
            Entropy values
        channel_names : list, optional
            Channel names
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        n_channels = len(Re_g_vals)
        if channel_names is None:
            channel_names = [f'Ch {i}' for i in range(n_channels)]
        
        x_vals = np.arange(n_channels)
        
        # Determine sleep state for each channel
        colors = []
        labels = []
        for re_g, e in zip(Re_g_vals, E_vals):
            if re_g > 2.0 and e > 2.5:
                colors.append(self.colors['wake_rem'])
                labels.append('Wake/REM')
            elif 1.0 < re_g <= 2.0 and 2.0 < e <= 2.5:
                colors.append(self.colors['light_sleep'])
                labels.append('Light Sleep')
            elif re_g <= 1.0 and e <= 2.0:
                colors.append(self.colors['deep_sleep'])
                labels.append('Deep Sleep')
            else:
                colors.append(self.colors['undetermined'])
                labels.append('Undetermined')
        
        # Create bars
        bars = ax.bar(x_vals, Re_g_vals, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        # Add value and state labels
        for i, (bar, val, label) in enumerate(zip(bars, Re_g_vals, labels)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{val:.2f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
            ax.text(bar.get_x() + bar.get_width()/2., height/2.,
                   label,
                   ha='center', va='center', fontweight='bold', fontsize=9, color='white')
        
        # Threshold lines
        ax.axhline(1.0, color='darkgreen', linestyle='--', linewidth=2, alpha=0.7, label='Re_g=1.0')
        ax.axhline(2.0, color='darkorange', linestyle='--', linewidth=2, alpha=0.7, label='Re_g=2.0')
        
        ax.set_xticks(x_vals)
        ax.set_xticklabels(channel_names, rotation=45, ha='right')
        ax.set_ylabel('Regularity Index (Re_g)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Channel', fontsize=12, fontweight='bold')
        ax.set_title('Regularity Index with Sleep State Classification', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['deep_sleep'], edgecolor='black', label='Deep Sleep (Re_g < 1.0)'),
            Patch(facecolor=self.colors['light_sleep'], edgecolor='black', label='Light Sleep (1.0 < Re_g < 2.0)'),
            Patch(facecolor=self.colors['wake_rem'], edgecolor='black', label='Wake/REM (Re_g > 2.0)'),
            Patch(facecolor=self.colors['undetermined'], edgecolor='black', label='Undetermined')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def plot_re_g_comparison(self, subjects: List[str],
                            re_g_means: List[float],
                            re_g_stds: List[float],
                            figsize: Tuple = (12, 6)):
        """
        Compare Re_g across multiple subjects
        
        Parameters:
        -----------
        subjects : list
            Subject identifiers
        re_g_means : list
            Mean Re_g per subject
        re_g_stds : list
            Std of Re_g per subject
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        x_vals = np.arange(len(subjects))
        
        # Error bars
        ax.bar(x_vals, re_g_means, yerr=re_g_stds, 
              capsize=5, alpha=0.7, color='steelblue', edgecolor='black', linewidth=1.5)
        
        # Threshold lines
        ax.axhline(1.0, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Deep Sleep')
        ax.axhline(2.0, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Light Sleep')
        
        ax.set_xticks(x_vals)
        ax.set_xticklabels(subjects, rotation=45, ha='right')
        ax.set_ylabel('Mean Regularity Index (±Std)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Subject', fontsize=12, fontweight='bold')
        ax.set_title('Regularity Index Comparison Across Subjects', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend()
        
        plt.tight_layout()
        return fig


# ============== EXAMPLE USAGE ==============

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REGULARITY INDEX VISUALIZATION EXAMPLES")
    print("="*80)
    
    # Generate sample data
    np.random.seed(42)
    n_channels = 4
    
    # Simulated metrics
    E_vals = np.array([2.1, 2.4, 1.9, 2.3])
    S_vals = np.array([0.45, 0.52, 0.48, 0.51])
    Re_g_vals = (E_vals ** 2) / S_vals
    
    channel_names = ['EEG-F3', 'EEG-F4', 'EEG-C3', 'EEG-C4']
    
    # Initialize visualizer
    viz = RegularityIndexVisualizer()
    
    # Example 1: Basic plot with thresholds
    print("\n[1] Creating Re_g plot with threshold lines...")
    fig1 = viz.plot_re_g_with_threshold(Re_g_vals, channel_names)
    fig1.savefig('01_re_g_with_thresholds.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 01_re_g_with_thresholds.png")
    
    # Example 2: Distribution
    print("\n[2] Creating Re_g distribution plot...")
    fig2 = viz.plot_re_g_distribution(Re_g_vals)
    fig2.savefig('02_re_g_distribution.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 02_re_g_distribution.png")
    
    # Example 3: E, S, Re_g comparison
    print("\n[3] Creating E, S, Re_g comparison...")
    fig3 = viz.plot_re_g_vs_entropy_connectivity(Re_g_vals, E_vals, S_vals, channel_names)
    fig3.savefig('03_e_s_reg_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 03_e_s_reg_comparison.png")
    
    # Example 4: Time series
    print("\n[4] Creating Re_g time series...")
    time_vals = np.linspace(0, 60, 200)
    re_g_time = 1.5 + 0.5 * np.sin(time_vals / 10) + 0.1 * np.random.randn(len(time_vals))
    fig4 = viz.plot_re_g_time_series(time_vals, re_g_time)
    fig4.savefig('04_re_g_timeseries.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 04_re_g_timeseries.png")
    
    # Example 5: Sleep state regions
    print("\n[5] Creating sleep state regions plot...")
    fig5 = viz.plot_re_g_sleep_state_regions(Re_g_vals, E_vals, channel_names)
    fig5.savefig('05_sleep_state_regions.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 05_sleep_state_regions.png")
    
    # Example 6: Subject comparison
    print("\n[6] Creating subject comparison...")
    subjects = ['sub-001', 'sub-002', 'sub-003', 'sub-004', 'sub-005']
    means = [1.2, 1.8, 2.3, 1.5, 2.1]
    stds = [0.3, 0.4, 0.35, 0.25, 0.4]
    fig6 = viz.plot_re_g_comparison(subjects, means, stds)
    fig6.savefig('06_subject_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 06_subject_comparison.png")
    
    print("\n" + "="*80)
    print("✓ ALL VISUALIZATIONS CREATED")
    print("="*80)
    
    # Print sample data
    print("\nSample Data:")
    print(f"Channels: {channel_names}")
    print(f"Entropy (E):      {E_vals}")
    print(f"Connectivity (S): {S_vals}")
    print(f"Regularity (Re_g): {Re_g_vals}")
    print(f"Formula: Re_g = E² / S")
