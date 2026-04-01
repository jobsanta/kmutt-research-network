import json
import pandas as pd

# 1. Load the source files
df_clusters = pd.read_csv('kmutt_professors_clustered.csv')
with open('kmutt_professors_full.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 2. Create helper mappings
name_to_cluster = df_clusters.set_index('Name')['Cluster'].to_dict()
# Map professor names to their Google Scholar links from the JSON
name_to_link = {p['name']: p.get('profile_link', '') for p in raw_data}

# Mapping for Theme Names based on Cluster IDs
suggestions = {
    0: "Cryptography & Image Security", 1: "Human-Computer Interaction", 2: "Environmental Ecology",
    3: "NLP", 4: "Nanotechnology", 5: "Wastewater Treatment", 6: "Nanomaterials",
    7: "Logistics", 8: "AI & Robotics", 9: "Food Engineering", 10: "Geotechnical Engineering",
    11: "Solar Energy", 12: "Cybersecurity", 13: "Data Science", 14: "English Teaching",
    15: "Wireless Power", 16: "Energy Policy", 17: "Power Electronics", 18: "Metallurgy",
    19: "Polymer Composites", 20: "Combustion", 21: "Telecommunications", 22: "Ed-Tech",
    23: "Finite Element Analysis", 24: "Sustainability & LCA", 25: "Organic Chemistry",
    26: "Applied Linguistics", 27: "Biomass", 28: "Remote Sensing", 29: "High Energy Physics",
    30: "3D Printing", 31: "Combinatorics", 32: "Food Microbiology", 33: "Conservation Ecology",
    34: "Applied Math", 35: "Chromatography", 36: "Material Science", 37: "Computer Vision",
    38: "Wind Energy", 39: "High Performance Computing", 40: "Biochemistry", 41: "Deep Learning",
    42: "Experimental Physics", 43: "Electrical Engineering", 44: "Convex Analysis",
    45: "Computer Graphics", 46: "Bioinformatics", 47: "Climate Change"
}

nodes = []
links = []
node_map = {}

def add_node(id_name, name, node_type, group, affiliation="", size=5, profile_link=""):
    if id_name not in node_map:
        node_map[id_name] = len(nodes)
        nodes.append({
            "id": id_name, 
            "name": name, 
            "type": node_type, 
            "group": group, 
            "affiliation": affiliation, 
            "size": size,
            "profile_link": profile_link
        })

# 3. Build the Network Structure
for prof in raw_data:
    name = prof['name']
    
    # Only process if they are a Primary Professor (found in CSV)
    if name in name_to_cluster:
        cid = int(name_to_cluster[name])
        cname = suggestions.get(cid, f"Cluster {cid}")
        p_link = prof.get('profile_link', '')
        
        # Add Theme Hub
        add_node(cname, cname, "hub", cid, size=20)
        
        # Add Professor (Primary)
        add_node(name, name, "prof", cid, affiliation="KMUTT", size=10, profile_link=p_link)
        
        # LINK: Hub <-> Professor (White)
        links.append({"source": cname, "target": name, "type": "theme-link"})
        
        # Process Co-authors
        for co in prof.get('co_authors', []):
            co_name = co['name']
            co_uni = co.get('university', 'Unknown')
            is_kmutt = any(k in co_uni.upper() for k in ["KMUTT", "KING MONGKUT", "THONBURI"])
            
            # CRITICAL FIX: Check if co-author is also a Primary Professor elsewhere
            if co_name in name_to_cluster:
                actual_cid = int(name_to_cluster[co_name])
                actual_cname = suggestions.get(actual_cid, f"Cluster {actual_cid}")
                co_link = name_to_link.get(co_name, co.get('link', '')) # Get their specific scholar link
                
                # Add them to THEIR own hub
                add_node(co_name, co_name, "prof", actual_cid, affiliation=co_uni, size=10, profile_link=co_link)
                add_node(actual_cname, actual_cname, "hub", actual_cid, size=20)
                links.append({"source": actual_cname, "target": co_name, "type": "theme-link"})
            else:
                # Regular secondary co-author
                co_type = "prof" if is_kmutt else "outside"
                add_node(co_name, co_name, co_type, cid, affiliation=co_uni, size=6, profile_link=co.get('link', ''))

            # LINK: Prof <-> Co-author (Internal=Green, External=Orange)
            l_type = "internal-link" if is_kmutt else "external-link"
            links.append({"source": name, "target": co_name, "type": l_type})

# 4. Save final JSON
with open('network_data.json', 'w', encoding='utf-8') as f:
    json.dump({"nodes": nodes, "links": links}, f, indent=4, ensure_ascii=False)

print(f"Successfully created network_data.json with {len(nodes)} nodes.")