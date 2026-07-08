"""
Early Warning Detector for Sleep Stage Transitions
Detects critical points and instability in Re_g timeseries

Author: EEG Analysis System
Date: 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal
from typing import Tuple, Dict, Optional, List

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 11


class EarlyWarningDetector:
    """Detect early warning signals for sleep stage transitions"""
    
    def __init__(self, critical_zone: float = 1.5, band: float = 0.2, window: int = 10):
        """
        Initialize Early Warning Detector
        
        Parameters:
        -----------
        critical_zone : float
            Center of critical zone (1.5 = boundary between Deep & Light Sleep)
        band : float
            Width around critical zone (±0.2)
        window : int
            Rolling window size
        """
        self.critical_zone = critical_zone
        self.band = band
        self.window = window
    
    def detect_early_warning(self, re_g_timeseries: np.ndarray) -> pd.DataFrame:
        """
        Detect early warning signals for stage transitions
        
        Your exact algorithm implementation:
        
        1. Rolling mean/std over window
        2. Trend (slope) detection
        3. Critical zone proximity
        4. Variance spike detection
        5. Persistence in critical zone
        6. Combined early warning signal
        
        Parameters:
        -----------
        re_g_timeseries : ndarray
            Time series of Re_g values
        
        Returns:
        --------
        df : DataFrame
            Analysis dataframe with warning signals
        """
        df = pd.DataFrame({"Re_g": re_g_timeseries})
        
        # --- Rolling statistics ---
        df["rolling_mean"] = df["Re_g"].rolling(self.window).mean()
        df["rolling_std"] = df["Re_g"].rolling(self.window).std()
        
        # --- Trend (slope) ---
        df["trend"] = df["Re_g"].diff()
        
        # --- Critical zone proximity ---
        CRITICAL = self.critical_zone
        BAND = self.band
        
        df["near_critical"] = (
            (df["Re_g"] > CRITICAL - BAND) &
            (df["Re_g"] < CRITICAL + BAND)
        )
        
        # --- Variance spike detection ---
        VAR_THRESHOLD = df["rolling_std"].mean()
        df["variance_spike"] = df["rolling_std"] > VAR_THRESHOLD
        
        # --- Persistence (critical slowing proxy) ---
        df["persistence"] = df["near_critical"].rolling(self.window).sum()
        
        # --- Final warning signal ---
        df["early_warning"] = (
            df["near_critical"] &
            df["variance_spike"] &
            (df["persistence"] > self.window/2)
        )
        
        return df
    
    def extract_warning_events(self, df: pd.DataFrame) -> List[Dict]:
        """
        Extract individual warning events from detection dataframe
        
        Parameters:
        -----------
        df : DataFrame
            Output from detect_early_warning
        
        Returns:
        --------
        events : list
            List of warning event dictionaries
        """
        events = []
        in_event = False
        event_start = None
        event_data = []
        
        for idx, row in df.iterrows():
            if row['early_warning'] and not in_event:
                # Event starts
                in_event = True
                event_start = idx
                event_data = [row]
            elif row['early_warning'] and in_event:
                # Event continues
                event_data.append(row)
            elif not row['early_warning'] and in_event:
                # Event ends
                in_event = False
                events.append({
                    'start_idx': event_start,
                    'end_idx': idx - 1,
                    'duration': idx - event_start,
                    'mean_re_g': np.mean([r['Re_g'] for r in event_data]),
                    'max_variance': np.max([r['rolling_std'] for r in event_data]),
                    'trend': np.mean([r['trend'] for r in event_data])
                })
                event_data = []
        
        # Handle event at end of series
        if in_event:
            events.append({
                'start_idx': event_start,
                'end_idx': len(df) - 1,
                'duration': len(df) - event_start,
                'mean_re_g': np.mean([r['Re_g'] for r in event_data]),
                'max_variance': np.max([r['rolling_std'] for r in event_data]),
                'trend': np.mean([r['trend'] for r in event_data])
            })
        
        return events
    
    def plot_early_warning_analysis(self, re_g_timeseries: np.ndarray,
                                    figsize: Tuple = (16, 10)) -> plt.Figure:
        """
        Comprehensive visualization of early warning signals
        
        Parameters:
        -----------
        re_g_timeseries : ndarray
            Time series of Re_g values
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        # Run detection
        df = self.detect_early_warning(re_g_timeseries)
        
        fig, axes = plt.subplots(5, 1, figsize=figsize, sharex=True)
        
        # Panel 1: Re_g timeseries with critical zone
        ax = axes[0]
        ax.plot(df.index, df["Re_g"], linewidth=2.5, color='steelblue', label='Re_g')
        ax.fill_between(df.index, self.critical_zone - self.band, 
                       self.critical_zone + self.band, 
                       alpha=0.2, color='orange', label='Critical Zone')
        ax.axhline(self.critical_zone, color='red', linestyle='--', linewidth=2,
                  label='Critical Threshold')
        ax.plot(df.index, df["rolling_mean"], linewidth=2, color='red', 
               linestyle=':', label='Rolling Mean')
        ax.set_ylabel('Re_g', fontweight='bold', fontsize=11)
        ax.set_title('Re_g Time Series with Critical Zone', fontweight='bold', fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Panel 2: Rolling statistics
        ax = axes[1]
        ax.fill_between(df.index, 0, df["rolling_std"], alpha=0.5, color='lightblue',
                       label='Rolling Std Dev')
        ax.axhline(df["rolling_std"].mean(), color='red', linestyle='--', linewidth=2,
                  label=f'Var Threshold ({df["rolling_std"].mean():.3f})')
        ax.scatter(df[df["variance_spike"]].index, df[df["variance_spike"]]["rolling_std"],
                  color='red', s=100, marker='X', label='Variance Spike', zorder=5)
        ax.set_ylabel('Rolling Std Dev', fontweight='bold', fontsize=11)
        ax.set_title('Variance Spike Detection', fontweight='bold', fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Panel 3: Trend
        ax = axes[2]
        colors = ['green' if x > 0 else 'red' for x in df["trend"]]
        ax.bar(df.index, df["trend"], color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        ax.set_ylabel('Trend (slope)', fontweight='bold', fontsize=11)
        ax.set_title('Re_g Trend (Positive=Increasing, Negative=Decreasing)', 
                    fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Panel 4: Persistence in critical zone
        ax = axes[3]
        ax.plot(df.index, df["persistence"], linewidth=2, color='purple', marker='o',
               markersize=4, label='Persistence Count')
        ax.axhline(self.window/2, color='orange', linestyle='--', linewidth=2,
                  label=f'Persistence Threshold ({self.window/2})')
        ax.fill_between(df.index, 0, self.window, alpha=0.1, color='purple')
        ax.set_ylabel('Persistence', fontweight='bold', fontsize=11)
        ax.set_title('Persistence in Critical Zone (Critical Slowing Proxy)', 
                    fontweight='bold', fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, self.window + 1])
        
        # Panel 5: Early warning signal
        ax = axes[4]
        near_crit = df[df["near_critical"]].index
        var_spike = df[df["variance_spike"]].index
        warning = df[df["early_warning"]].index
        
        ax.scatter(near_crit, [1]*len(near_crit), color='orange', s=100, 
                  marker='o', alpha=0.5, label='Near Critical Zone')
        ax.scatter(var_spike, [2]*len(var_spike), color='red', s=100,
                  marker='s', alpha=0.5, label='Variance Spike')
        ax.scatter(warning, [3]*len(warning), color='darkred', s=150,
                  marker='*', label='EARLY WARNING', zorder=5)
        
        ax.set_ylabel('Signal Type', fontweight='bold', fontsize=11)
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(['Critical', 'Variance', 'WARNING'])
        ax.set_title('Early Warning Signal (Combined)', fontweight='bold', fontsize=12)
        ax.set_ylim([0.5, 3.5])
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Overall x-label
        fig.text(0.5, 0.02, 'Time Index', ha='center', fontweight='bold', fontsize=12)
        
        plt.tight_layout(rect=[0, 0.03, 1, 1])
        return fig
    
    def plot_warning_events(self, re_g_timeseries: np.ndarray,
                           figsize: Tuple = (16, 6)) -> plt.Figure:
        """
        Highlight warning events on original timeseries
        
        Parameters:
        -----------
        re_g_timeseries : ndarray
            Time series of Re_g values
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        df = self.detect_early_warning(re_g_timeseries)
        events = self.extract_warning_events(df)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot timeseries
        ax.plot(df.index, df["Re_g"], linewidth=2.5, color='steelblue', 
               label='Re_g', marker='o', markersize=4)
        
        # Highlight warning events
        for i, event in enumerate(events):
            start = event['start_idx']
            end = event['end_idx']
            ax.axvspan(start, end, alpha=0.3, color='red',
                      label='Early Warning Event' if i == 0 else '')
            
            # Add annotation
            mid_point = (start + end) / 2
            ax.annotate(f'Event {i+1}', xy=(mid_point, df.loc[start, 'Re_g']),
                       xytext=(mid_point, df.loc[start, 'Re_g'] + 0.5),
                       ha='center', fontsize=10, fontweight='bold',
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        # Critical zone
        ax.fill_between(df.index, self.critical_zone - self.band,
                       self.critical_zone + self.band, alpha=0.1, color='orange',
                       label='Critical Zone')
        ax.axhline(self.critical_zone, color='red', linestyle='--', linewidth=2)
        
        # Labels
        ax.set_xlabel('Time Index', fontweight='bold', fontsize=12)
        ax.set_ylabel('Re_g', fontweight='bold', fontsize=12)
        ax.set_title('Early Warning Events in Re_g Timeseries', 
                    fontweight='bold', fontsize=14)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def print_warning_summary(self, re_g_timeseries: np.ndarray):
        """
        Print summary of early warning detection
        
        Parameters:
        -----------
        re_g_timeseries : ndarray
            Time series of Re_g values
        """
        df = self.detect_early_warning(re_g_timeseries)
        events = self.extract_warning_events(df)
        
        print("\n" + "="*80)
        print("EARLY WARNING DETECTOR SUMMARY")
        print("="*80)
        
        print(f"\nConfiguration:")
        print(f"  Critical Zone: {self.critical_zone} ± {self.band}")
        print(f"  Window Size: {self.window}")
        
        print(f"\nTimeseries Statistics:")
        print(f"  Length: {len(re_g_timeseries)} points")
        print(f"  Mean: {np.mean(re_g_timeseries):.4f}")
        print(f"  Std Dev: {np.std(re_g_timeseries):.4f}")
        print(f"  Range: [{np.min(re_g_timeseries):.4f}, {np.max(re_g_timeseries):.4f}]")
        
        print(f"\nDetection Results:")
        print(f"  Points near critical zone: {df['near_critical'].sum()}")
        print(f"  Variance spikes detected: {df['variance_spike'].sum()}")
        print(f"  Early warnings triggered: {df['early_warning'].sum()}")
        
        print(f"\nWarning Events: {len(events)}")
        for i, event in enumerate(events, 1):
            print(f"\n  Event {i}:")
            print(f"    Time range: {event['start_idx']} - {event['end_idx']}")
            print(f"    Duration: {event['duration']} points")
            print(f"    Mean Re_g: {event['mean_re_g']:.4f}")
            print(f"    Max Variance: {event['max_variance']:.4f}")
            print(f"    Trend: {event['trend']:.4f}")
        
        if len(events) == 0:
            print("\n  No early warning events detected")
        
        print(f"\nSignal Quality:")
        warning_rate = df['early_warning'].sum() / len(df) * 100
        print(f"  Warning event rate: {warning_rate:.2f}%")
        print(f"  Average persistence: {df['persistence'].mean():.2f}")
        
        print("\n" + "="*80)


# ============== EXAMPLE USAGE ==============

if __name__ == "__main__":
    print("\n" + "="*80)
    print("EARLY WARNING DETECTOR FOR SLEEP STAGE TRANSITIONS")
    print("="*80)
    
    # Simulate Re_g timeseries with transitions
    np.random.seed(42)
    n_points = 200
    
    # Create timeseries with stage transitions
    deep_sleep = np.random.normal(0.8, 0.1, 50)      # Deep sleep
    transition1 = np.linspace(0.8, 1.5, 30)          # Transition to light
    light_sleep = np.random.normal(1.5, 0.15, 50)    # Light sleep
    transition2 = np.linspace(1.5, 2.3, 30)          # Transition to wake
    wake = np.random.normal(2.5, 0.2, 40)            # Wake state
    
    re_g_timeseries = np.concatenate([deep_sleep, transition1, light_sleep, 
                                      transition2, wake])
    
    # Add noise
    re_g_timeseries += np.random.normal(0, 0.05, len(re_g_timeseries))
    re_g_timeseries = np.clip(re_g_timeseries, 0.1, 5.0)
    
    print(f"\nSimulated timeseries: {len(re_g_timeseries)} points")
    print("  Includes natural sleep stage transitions")
    
    # Initialize detector
    detector = EarlyWarningDetector(critical_zone=1.5, band=0.2, window=10)
    
    # Run detection
    print("\n[1] Running Early Warning Detection")
    print("-" * 80)
    df = detector.detect_early_warning(re_g_timeseries)
    print(f"✓ Detection complete")
    
    # Extract events
    print("\n[2] Extracting Warning Events")
    print("-" * 80)
    events = detector.extract_warning_events(df)
    print(f"✓ Found {len(events)} early warning events")
    
    # Generate visualizations
    print("\n[3] Generating Visualizations")
    print("-" * 80)
    
    fig1 = detector.plot_early_warning_analysis(re_g_timeseries)
    fig1.savefig('01_early_warning_analysis.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 01_early_warning_analysis.png")
    
    fig2 = detector.plot_warning_events(re_g_timeseries)
    fig2.savefig('02_warning_events.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: 02_warning_events.png")
    
    # Print summary
    print("\n[4] Summary Report")
    print("-" * 80)
    detector.print_warning_summary(re_g_timeseries)
    
    print("\n" + "="*80)
    print("✓ EARLY WARNING ANALYSIS COMPLETE")
    print("="*80)
