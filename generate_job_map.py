import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from adjustText import adjust_text
import io

# Data setup
target_counties = [
    'Austin', 'Brazoria', 'Chambers', 'Colorado', 'Fort Bend',
    'Galveston', 'Harris', 'Liberty', 'Matagorda', 'Montgomery',
    'Walker', 'Waller', 'Wharton'
]

job_fairs = {
    'Harris': [
        'Technical Industry Career Fair',
        'Healthcare Hiring Support',
        'Community, Education, & Social Service Hiring Event',
        'Production and Transportation Industry Hiring Event',
        'Bridges to Opportunity: Connecting Talent to Professional, Scientific & Technical Positions',
        'Installation, Maintenance, and Repair',
        'Connecting IT and Professional Careers Across Industries'
    ],
    'Fort Bend': [
        'Business & Financial Professionals Hiring Event'
    ],
    'Brazoria': [
        'Pearland Fall Hiring Event'
    ]
}

import textwrap

def generate_svg():
    # Load and filter counties
    print("Loading county shapefiles...")
    gdf_counties = gpd.read_file('tl_2025_us_county.shp')
    
    # Filter Texas and Louisiana counties
    tx_la_gdf = gdf_counties[gdf_counties['STATEFP'].isin(['48', '22'])].copy()
    tx_la_gdf = tx_la_gdf.to_crs(epsg=3857)
    
    # Target 13 counties
    region_gdf = tx_la_gdf[(tx_la_gdf['NAME'].isin(target_counties)) & (tx_la_gdf['STATEFP'] == '48')].copy()
    
    # Non-target counties (background)
    background_gdf = tx_la_gdf[~((tx_la_gdf['NAME'].isin(target_counties)) & (tx_la_gdf['STATEFP'] == '48'))].copy()
    
    # Visual settings
    fig, ax = plt.subplots(figsize=(24, 24))
    
    # Set Gulf background color (sea blue)
    ax.set_facecolor('#d9f2ff')
    fig.patch.set_facecolor('#d9f2ff')
    
    # Get Harris centroid for centering
    harris_centroid = region_gdf[region_gdf['NAME'] == 'Harris'].geometry.centroid.iloc[0]
    
    # Plot background counties (very light gray, no borders)
    background_gdf.plot(ax=ax, color='#f5f5f5', edgecolor='none', alpha=1.0, zorder=1)
    
    # Plot target counties with colors and borders
    region_gdf.plot(ax=ax, column='NAME', cmap='Set3', edgecolor='black', linewidth=1.5, alpha=0.9, zorder=2)
    
    # Set bounds centered on Harris County - Zoomed in closer with safe padding
    half_width = 300000  # Increased to 300km to ensure no callouts clip the borders
    ax.set_xlim(harris_centroid.x - half_width, harris_centroid.x + half_width)
    ax.set_ylim(harris_centroid.y - half_width, harris_centroid.y + half_width)
    
    # Add county names in white
    for idx, row in region_gdf.iterrows():
        name = row['NAME']
        centroid = row.geometry.centroid
        ax.text(centroid.x, centroid.y, name.upper(), 
                color='white', fontsize=26, weight='bold', ha='center',
                path_effects=[pe.withStroke(linewidth=3, foreground="#333333")],
                zorder=3)
        
        # Callouts for job fairs
        if name in job_fairs:
            # Smart wrapping: Bullets at start, indented following lines
            wrapped_list = []
            for event in job_fairs[name]:
                # Wrap each individual event line
                lines = textwrap.wrap(event, width=40 if name == 'Harris' else 50)
                if lines:
                    # First line gets the bullet
                    wrapped_list.append(f"• {lines[0]}")
                    # Subsequent lines get indented
                    for line in lines[1:]:
                        wrapped_list.append(f"  {line}")
            
            label = f"{name.upper()} COUNTY EVENTS:\n" + "\n".join(wrapped_list)
            
            # Specific offsets based on user request for positioning and no border interaction
            if name == 'Harris':
                # Moved left from previous 100k
                offset_x, offset_y = 60000, -105000
            elif name == 'Brazoria':
                # Slightly up to maintain hierarchy
                offset_x, offset_y = 0, -170000
            elif name == 'Fort Bend':
                # Moved up from previous -280k
                offset_x, offset_y = -30000, -220000
            
            # Align by top-left corner
            t_event = ax.text(centroid.x + offset_x, centroid.y + offset_y, label,
                         fontsize=22, color='black', weight='medium', 
                         va='top', ha='left',
                         bbox=dict(facecolor='white', alpha=0.95, edgecolor='gray', boxstyle='round,pad=0.5'),
                         zorder=4)
            
            # Draw line from centroid to callout
            ax.annotate('', xy=(centroid.x, centroid.y), xytext=(centroid.x + offset_x, centroid.y + offset_y),
                        arrowprops=dict(arrowstyle='->', color='gray', lw=2, connectionstyle="arc3,rad=0"),
                        zorder=4)

    ax.set_axis_off()
    plt.title("Workforce Solutions: Gulf Coast Region Job Fairs", fontsize=48, weight='bold', pad=20)
    
    # Save to SVG
    output_path = 'job_fair_map.svg'
    plt.savefig(output_path, format='svg', bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    generate_svg()
