"""
Quick test script to verify all modules work correctly
"""
from sefp.data import fetch_stock_data, NIFTY50_SYMBOLS
from sefp.indicators import (
    add_ema, add_rsi, add_adx, add_vwap,
    add_bollinger_bands, add_supertrend
)
from sefp.logic import analyze_sefp
from sefp.verdict import calculate_verdict
from sefp.llm_interpreter import format_verdict_for_llm, create_llm_request

def test_full_pipeline():
    """Test the complete SEFP pipeline"""
    print("=" * 60)
    print("Alpha Lens - Quick Test")
    print("=" * 60)
    
    # Use a reliable stock symbol
    test_symbol = "RELIANCE.NS"
    print(f"\n1. Fetching data for {test_symbol}...")
    
    try:
        df = fetch_stock_data(test_symbol)
        print(f"   ✓ Data fetched: {len(df)} rows")
        
        print("\n2. Calculating indicators...")
        df = add_ema(df)
        df = add_rsi(df)
        df = add_adx(df)
        df = add_vwap(df)
        df = add_bollinger_bands(df)
        df = add_supertrend(df)
        print("   ✓ All indicators calculated")
        
        print("\n3. Running SEFP analysis...")
        analysis = analyze_sefp(df)
        print(f"   ✓ Analysis complete")
        print(f"   - Trend valid: {analysis['trend_valid']}")
        print(f"   - Momentum: {analysis['momentum']}")
        print(f"   - Volume confirmed: {analysis['volume_confirmed']}")
        
        print("\n4. Calculating verdict...")
        verdict = calculate_verdict(analysis, df)
        print(f"   ✓ Verdict calculated")
        print(f"   - Score: {verdict['score']}/100")
        print(f"   - Action: {verdict['action']}")
        print(f"   - Reasoning: {verdict['reasoning'][:100]}...")
        
        print("\n5. Formatting for LLM...")
        llm_data = format_verdict_for_llm(test_symbol, analysis, verdict, df)
        llm_request = create_llm_request(test_symbol, analysis, verdict, df)
        print("   ✓ LLM data formatted")
        print(f"   - Stock: {llm_data['stock']}")
        print(f"   - Market regime: {llm_data['market_regime']}")
        print(f"   - Score: {llm_data['score']}")
        print(f"   - Action: {llm_data['action']}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! The app is ready to use.")
        print("=" * 60)
        print("\nTo run the Streamlit app, use:")
        print("  streamlit run app.py")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("3. Try a different stock symbol")
        raise

if __name__ == "__main__":
    test_full_pipeline()
