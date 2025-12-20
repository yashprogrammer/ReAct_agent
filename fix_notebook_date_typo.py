import json

file_path = '/Users/yashpatil/Developer/AI/Evolvue/ReAct_agent/experiment.ipynb'

try:
    with open(file_path, 'r') as f:
        data = json.load(f)

    changes_made = 0
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            new_source = []
            for line in cell.get('source', []):
                # Search for the specific typo line
                if 'for page in date.get("results",[]):' in line:
                    new_line = line.replace('date.get("results",[])', 'data.get("results",[])')
                    new_source.append(new_line)
                    changes_made += 1
                else:
                    new_source.append(line)
            cell['source'] = new_source

    if changes_made > 0:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=1)
        print(f"Successfully fixed {changes_made} occurrences of 'date.get' to 'data.get'.")
    else:
        print("No occurrences of 'date.get' typo found.")

except Exception as e:
    print(f"Error: {e}")
