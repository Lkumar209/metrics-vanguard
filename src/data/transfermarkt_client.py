import http.client
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from deep_translator import GoogleTranslator
from datetime import datetime
import numpy as np
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
import urllib.parse
import base64
from groq import Groq
from matplotlib.collections import LineCollection



class TransferMarktClient:
    def __init__(self):
        self.conn = http.client.HTTPSConnection("transfermarket.p.rapidapi.com")
        self.headers = {
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        self.translator = GoogleTranslator(source='auto', target='en')
        # self.groq_client = Groq(api_key="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")

    def search_player(self, query):
        try:
            self.conn.request("GET", f"/search?query={query}&domain=de", headers=self.headers)
            response = json.loads(self.conn.getresponse().read().decode("utf-8"))
            return response
        except Exception as e:
            print(f"Error searching player: {e}")
            return None
    
    def plot_market_value_history(self, market_data):
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(15, 8))
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        
        market_values = market_data.get('marketValueDevelopment', [])
        if market_values:
            # Parse dates and values correctly using unformattedDate and marketValueUnformatted
            dates = [datetime.strptime(mv['unformattedDate'], '%Y-%m-%d') for mv in market_values]
            values = [mv['marketValueUnformatted']/1000000 for mv in market_values]  # Convert to millions
            club_images = [mv.get('clubImage', '') for mv in market_values]
            
            # Plot line with gradient color based on value change
            values_norm = [(v - min(values))/(max(values) - min(values)) for v in values]
            points = np.array([dates, values]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            
            # Create color gradient
            cmap = plt.cm.RdYlGn  # Red to Green colormap
            lc = LineCollection(segments, cmap=cmap, norm=plt.Normalize(0, 1), zorder=1)
            lc.set_array(np.array(values_norm))
            line = ax.add_collection(lc)
            
            # Enhanced grid with custom styling
            plt.grid(True, linestyle='--', alpha=0.2, color='gray')
            
            # Add value labels and club logos with improved positioning
            for i, (date, value, logo_url) in enumerate(zip(dates, values, club_images)):
                # Alternate label positions to prevent overlap
                y_offset = 25 if i % 2 == 0 else -25
                
                # Add value label with enhanced styling
                plt.annotate(f'€{value:.1f}M', 
                            (date, value),
                            textcoords="offset points",
                            xytext=(0, y_offset),
                            ha='center',
                            color='#2c3e50',
                            bbox=dict(facecolor='white', 
                                    edgecolor='#bdc3c7',
                                    alpha=0.9,
                                    boxstyle='round,pad=0.5'),
                            fontsize=9,
                            zorder=3)
                
                # Add club logo with improved error handling
                if logo_url:
                    try:
                        response = requests.get(logo_url, timeout=5)
                        img = plt.imread(BytesIO(response.content))
                        imagebox = OffsetImage(img, zoom=0.2)  # Reduced logo size
                        ab = AnnotationBbox(imagebox, (date, value),
                                        frameon=False,
                                        box_alignment=(0.5, 0.5),
                                        pad=0,
                                        zorder=2)
                        plt.gca().add_artist(ab)
                    except Exception as e:
                        print(f"Error loading logo for date {date}: {e}")
            
            # Enhanced axes formatting
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_major_locator(mdates.YearLocator())
            plt.xticks(rotation=45, color='#2c3e50')
            plt.yticks(color='#2c3e50')
            
            # Add styled labels
            plt.ylabel("Market Value (€M)", fontsize=12, color='#2c3e50', fontweight='bold')
            
            # Add comprehensive trend analysis
            value_change = values[-1] - values[0]
            percent_change = (value_change / values[0]) * 100
            peak_value = max(values)
            peak_date = dates[values.index(peak_value)]
            
            trend_text = (
                f"Overall Change: {'↑' if value_change > 0 else '↓'} {abs(percent_change):.1f}%\n"
                f"Peak Value: €{peak_value:.1f}M ({peak_date.strftime('%Y-%m')})"
            )
            
            # Add trend text with styled box
            plt.figtext(0.02, 0.02, trend_text,
                    fontsize=10,
                    color='#2c3e50',
                    bbox=dict(facecolor='white',
                            edgecolor='#bdc3c7',
                            alpha=0.9,
                            boxstyle='round,pad=0.5'))
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_visible(False)
        
        # Save with improved quality
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight', 
                    facecolor='white', dpi=300)
        plt.close()
        img_buf.seek(0)
        return f"data:image/png;base64,{base64.b64encode(img_buf.getvalue()).decode()}"



    # def search_by_name(self, player_name):
    #     """Search player by name and return their ID"""
    #     try:
    #         # URL encode the player name
    #         encoded_name = urllib.parse.quote(player_name)
    #         self.conn.request("GET", f"/search/quick-search?query={encoded_name}&domain=de", headers=self.headers)
    #         response = json.loads(self.conn.getresponse().read().decode("utf-8"))
            
    #         # Get first player result
    #         if response and 'players' in response and response['players']:
    #             return response['players'][0]['id']
    #         return None
    #     except Exception as e:
    #         print(f"Error searching player: {e}")
    #         return None

    def search_by_name(self, player_name):
        """Search player by name and return their ID"""
        try:
            self.conn.request("GET", f"/search/quick-search?query={player_name}&domain=de", headers=self.headers)
            response = json.loads(self.conn.getresponse().read().decode("utf-8"))
            
            if response and 'players' in response and response['players']:
                return response['players'][0]['id']
            return None
        except Exception as e:
            print(f"Error searching player: {e}")
            return None


    def get_player_info(self, player_id):
        print("getting..")
        try:
            # Get basic info
            self.conn.request("GET", f"/players/get-header-info?id={player_id}&domain=de", headers=self.headers)
            basic_info = json.loads(self.conn.getresponse().read().decode("utf-8"))

            # Get market value
            self.conn.request("GET", f"/players/get-market-value?id={player_id}&domain=de", headers=self.headers)
            market_value = json.loads(self.conn.getresponse().read().decode("utf-8"))

            # Get transfer history
            self.conn.request("GET", f"/players/get-transfer-history?id={player_id}&domain=de", headers=self.headers)
            transfer_history = json.loads(self.conn.getresponse().read().decode("utf-8"))

            # Get performance data
            self.conn.request("GET", f"/players/get-performance-summary?id={player_id}&domain=de", headers=self.headers)
            performance = json.loads(self.conn.getresponse().read().decode("utf-8"))

            return {
                "basic_info": basic_info,
                "market_value": market_value,
                "transfer_history": transfer_history,
                "performance": performance
            }
        except Exception as e:
            print(f"Error fetching player data: {e}")
            return None

    def close_connection(self):
        self.conn.close()



# def plot_market_value_history(data):
#     # Set non-interactive backend
#     plt.switch_backend('Agg')
    
#     market_values = data['market_value']['marketValueDevelopment']
#     dates = [datetime.strptime(mv['unformattedDate'], '%Y-%m-%d') for mv in market_values]
#     values = [mv['marketValueUnformatted'] for mv in market_values]
    
#     fig, ax = plt.subplots(figsize=(15, 8))
#     ax.set_facecolor('#ffffff') 
#     fig.patch.set_facecolor('#ffffff')
    
#     plt.plot(dates, values, color='#00FF00', linewidth=2, zorder=1)
    
#     # Format axes and labels
#     plt.grid(True, linestyle='--', alpha=0.2, color='black')
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
#     plt.gca().xaxis.set_major_locator(mdates.YearLocator())
#     plt.xticks(color='black')
#     plt.yticks(color='black')
#     plt.ylabel("Market Value (€)", fontsize=12, color='black')
    
#     # Add value labels
#     for date, value in zip(dates, values):
#         plt.annotate(f'€{value/1000000:.1f}M', 
#                     (date, value),
#                     textcoords="offset points",
#                     xytext=(0, 10),
#                     ha='center',
#                     color='black')
    
#     plt.tight_layout()
#     return fig


# def plot_market_value_history(data):
#     # Set white background style
#     plt.style.use('default')
#     fig, ax = plt.subplots(figsize=(15, 8))
#     ax.set_facecolor('white')
#     fig.patch.set_facecolor('white')
    
#     market_values = data['market_value']['marketValueDevelopment']
#     dates = [datetime.strptime(mv['unformattedDate'], '%Y-%m-%d') for mv in market_values]
#     values = [mv['marketValueUnformatted'] for mv in market_values]
#     club_images = [mv.get('clubImage', '') for mv in market_values]
    
#     # Plot the main line
#     plt.plot(dates, values, color='#1e88e5', linewidth=2, zorder=1)
    
#     # Add grid with light gray color
#     plt.grid(True, linestyle='--', alpha=0.3, color='gray')
    
#     # Add logos and value labels
#     for i, (date, value, logo_url) in enumerate(zip(dates, values, club_images)):
#         try:
#             # Add value label above point
#             plt.annotate(f'€{value/1000000:.1f}M', 
#                         (date, value),
#                         textcoords="offset points",
#                         xytext=(0, 25),
#                         ha='center',
#                         va='bottom',
#                         fontsize=9,
#                         color='black',
#                         bbox=dict(facecolor='white', 
#                                 edgecolor='lightgray', 
#                                 alpha=0.9),
#                         zorder=3)
            
#             # Add club logo as data point
#             if logo_url:
#                 response = requests.get(logo_url)
#                 img = plt.imread(BytesIO(response.content))
#                 imagebox = OffsetImage(img, zoom=0.25)
#                 ab = AnnotationBbox(imagebox, 
#                                   (date, value),
#                                   frameon=False,
#                                   box_alignment=(0.5, 0.5),
#                                   pad=0,
#                                   zorder=2)
#                 plt.gca().add_artist(ab)
                
#         except Exception as e:
#             print(f"Error loading logo: {e}")
    
#     # Format axes
#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
#     plt.gca().xaxis.set_major_locator(mdates.YearLocator())
#     plt.xticks(color='black')
#     plt.yticks(color='black')
#     plt.ylabel("Market Value (€)", fontsize=12, color='black')
    
#     # Add trend analysis
#     value_change = values[-1] - values[0]
#     percent_change = (value_change / values[0]) * 100
#     trend_text = f"Overall Change: {'↑' if value_change > 0 else '↓'} {abs(percent_change):.1f}%"
#     plt.figtext(0.02, 0.02, trend_text, fontsize=10, color='black')
    
#     plt.tight_layout()
#     return fig





def format_player_data(data):
    if not data:
        return "No data available"

    translator = GoogleTranslator(source='auto', target='en')
    output = []
    
    # Basic Info
    player = data["basic_info"]["data"]["player"]
    club = data["basic_info"]["data"]["club"]
    
    output.append("## Basic Information")
    output.append(f"- Player ID: {player['id']}")
    output.append(f"- Name: {player['name']}")
    output.append(f"- Nationality: {translator.translate(player['nationalities'][0]['name'])}")
    output.append(f"- Current Club: {club['name']}")
    output.append(f"- Shirt Number: {player['shirtNumber']}\n")

    # Market Value
    output.append("## Market Value")
    current_value = player['marketValue']['value']
    output.append(f"**Current Value:** €{current_value:,}")
    
    output.append("\n**Market Value History:**")
    for value in data['market_value']['marketValueDevelopment'][:5]:
        formatted_value = f"€{value['marketValueUnformatted']:,}"
        club_name = translator.translate(value['clubName'])
        output.append(f"- {value['date']}: {formatted_value} ({club_name})")
    output.append("")

    # Transfer History
    output.append("## Transfer History")
    for transfer in data['transfer_history']['transferHistory']:
        date = transfer['date']
        old_club = translator.translate(transfer['oldClubName'])
        new_club = translator.translate(transfer['newClubName'])
        fee = transfer['transferFeeValue']
        if fee == "ablöse- frei":
            fee = "Free Transfer"
        elif fee == "-":
            fee = "No fee"
        else:
            fee = f"€{fee} {translator.translate(transfer['transferFeeNumeral'])}"
        output.append(f"- {date}: {old_club} → {new_club}")
        output.append(f"  Fee: {fee}\n")

    # Performance Statistics
    output.append("## 2023-2024 Season Statistics")
    for comp in data['performance']['competitionPerformanceSummery']:
        comp_name = translator.translate(comp['competition']['name'])
        if comp_name in ['Premier League', 'UEFA Champions League']:
            perf = comp['performance']
            output.append(f"\n**{comp_name}:**")
            output.append("| Statistic | Value |")
            output.append("|-----------|--------|")
            output.append(f"| Appearances | {perf['matches']} |")
            output.append(f"| Goals | {perf['goals']} |")
            output.append(f"| Assists | {perf['assists']} |")
            output.append(f"| Minutes Played | {perf['minutesPlayed']} |")
            if int(perf['yellowCards']) > 0:
                output.append(f"| Yellow Cards | {perf['yellowCards']} |")
            if int(perf['redCards']) > 0:
                output.append(f"| Red Cards | {perf['redCards']} |")

    # Generate market value history plot
    # plot_market_value_history(data)

    return "\n".join(output)
