import json
import xmltodict

# FILENAME = "/Users/smacpher/clones/tmpl_venv/acm_corpus/proceedings/PROC-SLIP03-2003-639929.xml"
FILENAME = "/Users/smacpher/clones/tmpl_venv/acm_corpus/proceedings/test.xml"
if __name__ == "__main__":
    result = xmltodict.parse(FILENAME)
    print(json.dumps(result, indent=4))
    
