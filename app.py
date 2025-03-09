import streamlit as st
import pubchempy as pcp
import wikipediaapi
from rdkit import Chem
from rdkit.Chem import Descriptors

# Wikipedia function
def get_wikipedia_summary(smiles):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')

    try:
        compound = pcp.get_compounds(smiles, 'smiles')
        query = compound[0].iupac_name if compound else smiles  # Use IUPAC Name if available
    except:
        query = smiles  

    try:
        page = wiki_wiki.page(query)
        if page.exists():
            summary = page.summary.split("==")[0].strip()  # Remove unwanted sections
            return summary, page.fullurl, query  # Return query to improve PubChem search
        return "No Wikipedia summary available.", None, None
    except Exception as e:
        return f"Error retrieving Wikipedia data: {str(e)}", None, None

# Updated PubChem function with CID and link
def get_pubchem_data(smiles, iupac_fallback=None):
    try:
        compounds = pcp.get_compounds(smiles, 'smiles')
        if not compounds and iupac_fallback:
            compounds = pcp.get_compounds(iupac_fallback, 'name')

        if not compounds:
            return None

        compound = compounds[0]
        pubchem_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}"
        return {
            "Molecular Formula": compound.molecular_formula,
            "Molecular Weight": f"{compound.molecular_weight} g/mol",
            "IUPAC Name": compound.iupac_name,
            "Canonical SMILES": compound.canonical_smiles,
            "PubChem Link": pubchem_url  # Added PubChem URL
        }
    except Exception as e:
        return None

# Compute molecular properties
def get_molecule_info(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return "Invalid SMILES string."

    mol_weight = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    
    wiki_summary, wiki_url, wiki_iupac = get_wikipedia_summary(smiles)
    pubchem_data = get_pubchem_data(smiles, wiki_iupac)  # Try SMILES, then IUPAC Name

    return {
        "SMILES": smiles,
        "Molecular Weight": f"{mol_weight:.2f} g/mol",
        "logP": f"{logp:.2f}",
        "Wikipedia Summary": wiki_summary,
        "Wikipedia Link": wiki_url,
        "PubChem Data": pubchem_data,
    }

# Streamlit UI
st.title("🔬 Molecule Information Finder")
st.write("Enter a **SMILES** string to retrieve molecular properties, Wikipedia summary, and PubChem data.")
st.write("Example: Aspirin - `CC(=O)OC1=CC=CC=C1C(=O)O`")

# User input
smiles_input = st.text_input("Enter SMILES structure", "")

if smiles_input:
    info = get_molecule_info(smiles_input)
    
    if isinstance(info, str):
        st.error(info)
    else:
        st.success("Results retrieved successfully!")
        
        st.subheader("Molecular Properties")
        st.write(f"**Molecular Weight:** {info['Molecular Weight']}")
        st.write(f"**logP:** {info['logP']}")

        st.subheader("Wikipedia Summary")
        st.write(info["Wikipedia Summary"])
        if info["Wikipedia Link"]:
            st.markdown(f"[🔗 View on Wikipedia]({info['Wikipedia Link']})", unsafe_allow_html=True)

        st.subheader("PubChem Data")
        if info["PubChem Data"]:
            st.write(f"**Molecular Formula:** {info['PubChem Data']['Molecular Formula']}")
            st.write(f"**Molecular Weight:** {info['PubChem Data']['Molecular Weight']}")
            st.write(f"**IUPAC Name:** {info['PubChem Data']['IUPAC Name']}")
            st.write(f"**Canonical SMILES:** {info['PubChem Data']['Canonical SMILES']}")
            st.markdown(f"[🔗 View on PubChem]({info['PubChem Data']['PubChem Link']})", unsafe_allow_html=True)
        else:
            st.warning("No PubChem data found. Try a different SMILES.")