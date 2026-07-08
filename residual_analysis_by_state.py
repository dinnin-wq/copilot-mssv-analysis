"""
Residual Analysis with Sleep State Visualization
Scatter plots of residuals colored by sleep state classification

Author: EEG Analysis System
Date: 2025
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from typing import List, Optional, Tuple, Dict


class ResidualAnalysisByState:
    """Analyze model residuals colored by sleep state"""
    
    def __init__(self):
        """Initialize visualizer"""
        self.colors_map = {
            'Wake/REM': '#FF6B6B',        # Red
            'Light Sleep': '#FFD93D',     # Yellow
            'Deep Sleep': '#6BCB77',      # Green
            'Undetermined': '#A8A8A8'     # Gray
        }
        self.model = None
        self.residuals = None
    
    def fit_regression(self, E_vals: np.ndarray, S_vals: np.ndarray) -> Tuple:
        """
        Fit OLS regression: log(Re_g) = β₀ + β₁·log(E) + β₂·log(S)
        
        Parameters:
        -----------
        E_vals : ndarray
            Entropy values
        S_vals : ndarray
            Connectivity values
        
        Returns:
        --------
        model : OLS model object
        log_E : ndarray
            Log-transformed entropy
        residuals : ndarray
            Model residuals
        """
        # Compute Re_g
        Re_g_vals = (E_vals**2) / (S_vals + 1e-8)
        
        # Log transform
        log_E = np.log(E_vals)
        log_S = np.log(S_vals + 1e-8)
        log_Re_g = np.log(Re_g_vals)
        
        # Fit model
        X = np.column_stack([log_E, log_S])
        X = sm.add_constant(X)
        
        self.model = sm.OLS(log_Re_g, X).fit()
        self.residuals = self.model.resid
        self.log_E = log_E
        
        return self.model, log_E, self.residuals
    
    def classify_sleep_state(self, E_vals: np.ndarray, 
                            S_vals: np.ndarray) -> List[str]:
        """
        Classify sleep state for each channel
        
        Parameters:
        -----------
        E_vals : ndarray
            Entropy values
        S_vals : ndarray
            Connectivity values
        
        Returns:
        --------
        states : list
            Sleep state labels
        """
        Re_g_vals = (E_vals**2) / (S_vals + 1e-8)
        states = []
        
        for re_g, e in zip(Re_g_vals, E_vals):
            if re_g > 2.0 and e > 2.5:
                states.append('Wake/REM')
            elif 1.0 < re_g <= 2.0 and 2.0 < e <= 2.5:
                states.append('Light Sleep')
            elif re_g <= 1.0 and e <= 2.0:
                states.append('Deep Sleep')
            else:
                states.append('Undetermined')
        
        return states
    
    def plot_residuals_by_state(self, log_E: np.ndarray,
                               residuals: np.ndarray,
                               state_labels: List[str],
                               figsize: Tuple = (14, 6),
                               title: str = "Residuals vs log(E) colored by Sleep State"):
        """
        Main visualization: scatter plot of residuals colored by sleep state
        
        Implements:
        plt.scatter(log_E, residuals, c=state_labels)
        
        Parameters:
        -----------
        log_E : ndarray
            Log-transformed entropy
        residuals : ndarray
            Model residuals
        state_labels : list
            Sleep state labels per channel
        figsize : tuple
            Figure size
        title : str
            Plot title
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create color array
        colors = [self.colors_map.get(state, '#A8A8A8') for state in state_labels]
        
        # Scatter plot
        scatter = ax.scatter(log_E, residuals, c=colors, s=200, 
                           alpha=0.7, edgecolors='black', linewidth=1.5)
        
        # Reference lines
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2, 
                  label='Perfect fit (residual=0)')
        ax.axhline(y=residuals.std(), color='orange', linestyle=':', linewidth=1.5,
                  label=f'±1 Std Dev (±{residuals.std():.3f})')
        ax.axhline(y=-residuals.std(), color='orange', linestyle=':', linewidth=1.5)
        
        # Labels and formatting
        ax.set_xlabel('log(Entropy)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residuals', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors_map['Deep Sleep'], edgecolor='black', 
                 label='Deep Sleep (Re_g < 1.0)'),
            Patch(facecolor=self.colors_map['Light Sleep'], edgecolor='black',
                 label='Light Sleep (1.0 < Re_g < 2.0)'),
            Patch(facecolor=self.colors_map['Wake/REM'], edgecolor='black',
                 label='Wake/REM (Re_g > 2.0)'),
            Patch(facecolor=self.colors_map['Undetermined'], edgecolor='black',
                 label='Undetermined')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def plot_residuals_by_fitted(self, fitted_values: np.ndarray,
                                residuals: np.ndarray,
                                state_labels: List[str],
                                figsize: Tuple = (14, 6)):
        """
        Scatter plot of residuals vs fitted values colored by sleep state
        
        Parameters:
        -----------
        fitted_values : ndarray
            Model fitted values
        residuals : ndarray
            Model residuals
        state_labels : list
            Sleep state labels
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create color array
        colors = [self.colors_map.get(state, '#A8A8A8') for state in state_labels]
        
        # Scatter plot
        ax.scatter(fitted_values, residuals, c=colors, s=200,
                  alpha=0.7, edgecolors='black', linewidth=1.5)
        
        # Reference line
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2,
                  label='Perfect fit')
        
        # Labels
        ax.set_xlabel('Fitted Values (log(Re_g))', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residuals', fontsize=12, fontweight='bold')
        ax.set_title('Residuals vs Fitted Values by Sleep State', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_qq_by_state(self, residuals: np.ndarray,
                        state_labels: List[str],
                        figsize: Tuple = (14, 6)):
        """
        Q-Q plot with points colored by sleep state
        
        Parameters:
        -----------
        residuals : ndarray
            Model residuals
        state_labels : list
            Sleep state labels
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Compute theoretical quantiles
        theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(residuals)))
        sample_quantiles = np.sort(residuals)
        
        # Create color array
        sorted_indices = np.argsort(residuals)
        sorted_states = [state_labels[i] for i in sorted_indices]
        colors = [self.colors_map.get(state, '#A8A8A8') for state in sorted_states]
        
        # Plot
        ax.scatter(theoretical_quantiles, sample_quantiles, c=colors, s=200,
                  alpha=0.7, edgecolors='black', linewidth=1.5)
        
        # Reference line (perfect normality)
        min_val = min(theoretical_quantiles.min(), sample_quantiles.min())
        max_val = max(theoretical_quantiles.max(), sample_quantiles.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2,
               label='Perfect normality')
        
        # Labels
        ax.set_xlabel('Theoretical Quantiles', fontsize=12, fontweight='bold')
        ax.set_ylabel('Sample Quantiles', fontsize=12, fontweight='bold')
        ax.set_title('Q-Q Plot by Sleep State', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_residuals_distribution_by_state(self, residuals: np.ndarray,
                                            state_labels: List[str],
                                            figsize: Tuple = (14, 6)):
        """
        Histogram of residuals with separate colors for each sleep state
        
        Parameters:
        -----------
        residuals : ndarray
            Model residuals
        state_labels : list
            Sleep state labels
        figsize : tuple
            Figure size
        
        Returns:
        --------
        fig : Figure
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Separate residuals by state
        states_unique = sorted(set(state_labels))
        
        for state in states_unique:
            mask = np.array(state_labels) == state
            state_residuals = residuals[mask]
            color = self.colors_map.get(state, '#A8A8A8')
            
            ax.hist(state_residuals, alpha=0.5, label=state, color=color,
                   edgecolor='black', bins=10)
        
        # Reference line at 0
        ax.axvline(x=0, color='red', linestyle='--', linewidth=2,
                  label='Perfect fit')
        
        # Labels
        ax.set_xlabel('Residuals', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Distribution of Residuals by Sleep State',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig
    
    def print_residual_statistics_by_state(self, residuals: np.ndarray,
                                          state_labels: List[str]):
        """
        Print residual statistics grouped by sleep state
        
        Parameters:
        -----------
        residuals : ndarray
            Model residuals
        state_labels : list
            Sleep state labels
        """
        print("\n" + "="*80)
        print("RESIDUAL STATISTICS BY SLEEP STATE")
        print("="*80)
        
        states_unique = sorted(set(state_labels))
        
        for state in states_unique:
            mask = np.array(state_labels) == state
            state_residuals = residuals[mask]
            
            print(f"\n{state}:")
            print(f"  n                = {len(state_residuals)}")
            print(f"  Mean             = {np.mean(state_residuals):.6f}")
            print(f"  Std Dev          = {np.std(state_residuals):.6f}")
            print(f"  Min              = {np.min(state_residuals):.6f}")
            print(f"  Max              = {np.max(state_residuals):.6f}")
            print(f"  Median           = {np.median(state_residuals):.6f}")
            print(f"  Q25-Q75          = [{np.percentile(state_residuals, 25):.6f}, "
                  f"{np.percentile(state_residuals, 75):.6f}]")
        
        print("\n" + "="*80)


# ============== EXAMPLE USAGE ==============

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RESIDUAL ANALYSIS WITH SLEEP STATE VISUALIZATION")
    print("="*80)
    
    # Generate sample data
    np.random.seed(42)
    n_channels = 92
    
    # Simulated metrics (following Re_g = E²/S formula with some noise)
    E_vals = np.random.uniform(1.5, 3.0, n_channels)
    S_vals = np.random.uniform(0.3, 0.8, n_channels)
    
    # Add some noise to violate the formula slightly
    noise = np.random.normal(0, 0.05, n_channels)
    S_vals = S_vals + noise
    
    # Initialize analyzer
    analyzer = ResidualAnalysisByState()
    
    # Fit regression
    print("\n[1] Fitting OLS Regression Model")
    print("-" * 80)
    model, log_E, residuals = analyzer.fit_regression(E_vals, S_vals)
    print(model.summary())
    
    # Classify sleep states
    print("\n[2] Classifying Sleep States")
    print("-" * 80)
    state_labels = analyzer.classify_sleep_state(E_vals, S_vals)
    
    # Count by state
    from collections import Counter
    state_counts = Counter(state_labels)
    for state, count in sorted(state_counts.items()):
        print(f"  {state}: {count} channels")
    
    # Generate visualizations
    print("\n[3] Creating Visualizations")
    print("-" * 80)
    
    # Plot 1: Main residual plot (your exact request!)
    print("  - Creating: Residuals vs log(E) colored by state")
    fig1 = analyzer.plot_residuals_by_state(log_E, residuals, state_labels)
    fig1.savefig('01_residuals_by_state.png', dpi=150, bbox_inches='tight')
    print("    ✓ Saved: 01_residuals_by_state.png")
    
    # Plot 2: Residuals vs fitted
    print("  - Creating: Residuals vs fitted values")
    fitted_values = model.fittedvalues
    fig2 = analyzer.plot_residuals_by_fitted(fitted_values, residuals, state_labels)
    fig2.savefig('02_residuals_vs_fitted.png', dpi=150, bbox_inches='tight')
    print("    ✓ Saved: 02_residuals_vs_fitted.png")
    
    # Plot 3: Q-Q plot
    print("  - Creating: Q-Q plot by state")
    fig3 = analyzer.plot_qq_by_state(residuals, state_labels)
    fig3.savefig('03_qq_plot_by_state.png', dpi=150, bbox_inches='tight')
    print("    ✓ Saved: 03_qq_plot_by_state.png")
    
    # Plot 4: Distribution
    print("  - Creating: Residual distributions by state")
    fig4 = analyzer.plot_residuals_distribution_by_state(residuals, state_labels)
    fig4.savefig('04_residuals_distribution.png', dpi=150, bbox_inches='tight')
    print("    ✓ Saved: 04_residuals_distribution.png")
    
    # Print statistics
    print("\n[4] Computing Statistics")
    print("-" * 80)
    analyzer.print_residual_statistics_by_state(residuals, state_labels)
    
    print("\n" + "="*80)
    print("✓ ANALYSIS COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  1. 01_residuals_by_state.png - Main scatter plot")
    print("  2. 02_residuals_vs_fitted.png - Residuals vs fitted")
    print("  3. 03_qq_plot_by_state.png - Normality check")
    print("  4. 04_residuals_distribution.png - Distribution by state")
