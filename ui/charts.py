"""
Charts Module
Specialized chart creation functions for portfolio visualization
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta


def create_portfolio_composition_chart(portfolio_data: List[Dict]) -> go.Figure:
    """Create portfolio composition pie chart"""
    if not portfolio_data:
        return go.Figure()

    df = pd.DataFrame(portfolio_data)

    # Group by sector
    sector_data = df.groupby('sector')['total_value'].sum().reset_index()

    fig = px.pie(
        sector_data,
        values='total_value',
        names='sector',
        title="Portfolio Composition by Sector",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )

    return fig


def create_performance_chart(portfolio_data: List[Dict]) -> go.Figure:
    """Create stock performance bar chart"""
    if not portfolio_data:
        return go.Figure()

    df = pd.DataFrame(portfolio_data)

    # Sort by gain/loss percentage
    df_sorted = df.sort_values('gain_loss_percent', ascending=True)

    # Create color scale based on performance
    colors = ['red' if x < 0 else 'green' for x in df_sorted['gain_loss_percent']]

    fig = go.Figure(data=[
        go.Bar(
            x=df_sorted['Ticker'],
            y=df_sorted['gain_loss_percent'],
            marker_color=colors,
            text=[f"{x:.2f}%" for x in df_sorted['gain_loss_percent']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Gain/Loss: %{y:.2f}%<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Stock Performance (Gain/Loss %)",
        xaxis_title="Ticker",
        yaxis_title="Gain/Loss (%)",
        xaxis_tickangle=-45,
        showlegend=False,
        yaxis=dict(zeroline=True, zerolinecolor='black', zerolinewidth=1)
    )

    return fig


def create_dividend_analysis_chart(portfolio_data: List[Dict]) -> go.Figure:
    """Create dividend analysis chart"""
    if not portfolio_data:
        return go.Figure()

    df = pd.DataFrame(portfolio_data)

    # Filter stocks with dividends
    dividend_stocks = df[df['Dividend Yield'].str.replace('%', '').astype(float) > 0]

    if dividend_stocks.empty:
        return go.Figure()

    fig = go.Figure(data=[
        go.Bar(
            x=dividend_stocks['Ticker'],
            y=dividend_stocks['Dividend Yield'].str.replace('%', '').astype(float),
            marker_color='lightblue',
            text=[f"{x:.2f}%" for x in dividend_stocks['Dividend Yield'].str.replace('%', '').astype(float)],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Dividend Yield: %{y:.2f}%<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Dividend Yield by Stock",
        xaxis_title="Ticker",
        yaxis_title="Dividend Yield (%)",
        xaxis_tickangle=-45,
        showlegend=False
    )

    return fig


def create_annual_dividend_chart(portfolio_data: List[Dict]) -> go.Figure:
    """Create annual dividend income chart"""
    if not portfolio_data:
        return go.Figure()

    df = pd.DataFrame(portfolio_data)

    # Filter stocks with dividends
    dividend_stocks = df[df['annual_dividend'] > 0]

    if dividend_stocks.empty:
        return go.Figure()

    fig = go.Figure(data=[
        go.Bar(
            x=dividend_stocks['Ticker'],
            y=dividend_stocks['annual_dividend'],
            marker_color='gold',
            text=[f"${x:.2f}" for x in dividend_stocks['annual_dividend']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Annual Dividend: $%{y:.2f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Annual Dividend Income by Stock",
        xaxis_title="Ticker",
        yaxis_title="Annual Dividend ($)",
        xaxis_tickangle=-45,
        showlegend=False
    )

    return fig


def create_sector_value_chart(sectors: Dict) -> go.Figure:
    """Create sector value distribution chart"""
    if not sectors:
        return go.Figure()

    # Convert sectors dict to DataFrame
    sector_data = []
    for sector, data in sectors.items():
        sector_data.append({
            'Sector': sector,
            'Value': data.get('value', 0),
            'Percentage': data.get('percentage', 0),
            'Count': data.get('count', 0)
        })

    df = pd.DataFrame(sector_data)
    df_sorted = df.sort_values('Value', ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            x=df_sorted['Value'],
            y=df_sorted['Sector'],
            orientation='h',
            marker_color='lightgreen',
            text=[f"${x:,.2f} ({y:.1f}%)" for x, y in zip(df_sorted['Value'], df_sorted['Percentage'])],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Value: $%{x:,.2f}<br>Percentage: %{customdata:.1f}%<extra></extra>',
            customdata=df_sorted['Percentage']
        )
    ])

    fig.update_layout(
        title="Portfolio Value by Sector",
        xaxis_title="Value ($)",
        yaxis_title="Sector",
        showlegend=False
    )

    return fig


def create_risk_return_chart(portfolio_data: List[Dict]) -> go.Figure:
    """Create risk-return scatter plot"""
    if not portfolio_data:
        return go.Figure()

    df = pd.DataFrame(portfolio_data)

    # Calculate risk metrics for each stock (simplified)
    df['risk'] = df['gain_loss_percent'].abs()  # Simplified risk measure
    df['return'] = df['gain_loss_percent']
    df['size'] = df['total_value']  # Bubble size based on position value

    fig = px.scatter(
        df,
        x='risk',
        y='return',
        size='size',
        hover_name='Ticker',
        title="Risk vs Return Analysis",
        labels={'risk': 'Risk (Absolute Return %)', 'return': 'Return (%)'},
        color='sector',
        size_max=50
    )

    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=0, line_dash="dash", line_color="gray")

    return fig


def create_portfolio_timeline_chart(portfolio_data: List[Dict]) -> go.Figure:
    """Create portfolio timeline chart (mock data for demonstration)"""
    if not portfolio_data:
        return go.Figure()

    # Generate mock timeline data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')

    # Mock portfolio value progression
    base_value = sum(stock.get('total_value', 0) for stock in portfolio_data)
    values = []
    current_value = base_value * 0.8  # Start 20% lower

    for i, date in enumerate(dates):
        # Add some random variation
        variation = (i * 0.5) + (i % 7 - 3) * 0.1
        current_value = base_value * (0.8 + variation * 0.1)
        values.append(max(current_value, base_value * 0.5))  # Don't go below 50% of base

    fig = go.Figure(data=[
        go.Scatter(
            x=dates,
            y=values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='blue', width=2),
            hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title="Portfolio Value Timeline (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        showlegend=False
    )

    return fig
