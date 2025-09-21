from app import app, db, ScriptExecution
import json

def extract_btst_json():
    with app.app_context():
        ex = ScriptExecution.query.filter_by(id=57).first()
        if ex and ex.output:
            # Save raw output to file for analysis
            with open('btst_raw_output.txt', 'w') as f:
                f.write(ex.output)
            print('Raw output saved to btst_raw_output.txt')
            print('Output length:', len(ex.output))
            
            # Try to find JSON section
            output = ex.output
            json_start = output.find('{"metadata"')
            if json_start == -1:
                json_start = output.find('{')
            
            if json_start != -1:
                json_text = output[json_start:]
                # Find the last complete JSON
                last_brace = json_text.rfind('}')
                if last_brace != -1:
                    json_text = json_text[:last_brace+1]
                    try:
                        json_data = json.loads(json_text)
                        print('JSON parsed successfully!')
                        print('Keys:', list(json_data.keys()))
                        
                        # Save clean JSON
                        with open('btst_sample_output.json', 'w') as f:
                            json.dump(json_data, f, indent=2)
                        print('Clean JSON saved to btst_sample_output.json')
                        
                        # Show structure
                        if 'metadata' in json_data:
                            meta = json_data['metadata']
                            print(f'Total stocks: {meta.get("total_stocks_analyzed", 0)}')
                            print(f'Actionable recommendations: {meta.get("actionable_recommendations", 0)}')
                            print(f'BTST opportunities: {meta.get("btst_opportunities", 0)}')
                        
                        return json_data
                    except Exception as e:
                        print('JSON parse error:', str(e))
                        print('First 500 chars of JSON text:')
                        print(json_text[:500])
            else:
                print('No JSON found in output')
        else:
            print('No execution found with ID 57')

if __name__ == "__main__":
    extract_btst_json()
