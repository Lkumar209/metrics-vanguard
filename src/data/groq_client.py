# # src/data/groq_client.py
# from groq import Groq
# import json

# class SportsDataClient:
#     def __init__(self):
#         self.client = Groq(api_key="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")
#         self.model = "llama3-70b-8192"

#     def fetch_player_data(self, player_name):
#         messages = [
#             {
#                 "role": "system",
#                 "content": """You are a sports data analyst. Return detailed player data in JSON format with the following structure:
#                 {
#                     "player": {
#                         "name": string,
#                         "position": string,
#                         "nationality": string,
#                         "dateOfBirth": string,
#                         "height": number,
#                         "weight": number,
#                         "currentTeam": string
#                     },
#                     "marketValue": {
#                         "current": number,
#                         "history": [
#                             {
#                                 "date": string,
#                                 "value": number
#                             }
#                         ]
#                     },
#                     "transferHistory": [
#                         {
#                             "date": string,
#                             "from": string,
#                             "to": string,
#                             "fee": number
#                         }
#                     ],
#                     "performanceMetrics": {
#                         "currentSeason": {
#                             "appearances": number,
#                             "goals": number,
#                             "assists": number,
#                             "minutesPlayed": number
#                         },
#                         "goalsPer90": [
#                             {
#                                 "season": string,
#                                 "value": number
#                             }
#                         ],
#                         "shotsPer90": [
#                             {
#                                 "season": string,
#                                 "value": number
#                             }
#                         ],
#                         "passSuccessRate": [
#                             {
#                                 "season": string,
#                                 "value": number
#                             }
#                         ]
#                     }
#                 }"""
#             },
#             {
#                 "role": "user",
#                 "content": f"Get detailed stats and market value data for {player_name} in JSON format, including current 2023-2024 season data."
#             }
#         ]

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=0.7,
#                 max_tokens=2000,
#                 response_format={"type": "json_object"}
#             )
#             return json.loads(response.choices[0].message.content)
#         except Exception as e:
#             print(f"Error fetching data: {e}")
#             return None

# def format_player_data(data):
#     output = []
    
#     # Player Profile
#     output.append("## Player Profile")
#     player = data["player"]
#     output.append(f"**Name:** {player['name']}")
#     output.append(f"**Position:** {player['position']}")
#     output.append(f"**Nationality:** {player['nationality']}")
#     output.append(f"**Date of Birth:** {player['dateOfBirth']}")
#     output.append(f"**Height:** {player['height']} cm")
#     output.append(f"**Weight:** {player['weight']} kg")
#     output.append(f"**Current Team:** {player['currentTeam']}\n")

#     # Market Value
#     output.append("## Market Value")
#     output.append(f"**Current Value:** €{data['marketValue']['current']:,}")
#     output.append("\n**Historical Values:**")
#     for value in data['marketValue']['history']:
#         output.append(f"- {value['date']}: €{value['value']:,}")
#     output.append("")

#     # Transfer History
#     output.append("## Transfer History")
#     for i, transfer in enumerate(data['transferHistory'], 1):
#         output.append(f"{i}. **{transfer['to']}** ({transfer['date']})")
#         output.append(f"   - From: {transfer['from']}")
#         output.append(f"   - Fee: €{transfer['fee']:,}\n")

#     # Current Season Performance
#     output.append("## 2023-2024 Season Statistics")
#     current = data['performanceMetrics']['currentSeason']
#     output.append("| Statistic | Value |")
#     output.append("|-----------|--------|")
#     output.append(f"| Appearances | {current['appearances']} |")
#     output.append(f"| Goals | {current['goals']} |")
#     output.append(f"| Assists | {current['assists']} |")
#     output.append(f"| Minutes Played | {current['minutesPlayed']} |\n")

#     # Historical Performance Metrics
#     output.append("## Performance Metrics\n")
#     metrics = [
#         ("Goals per 90 Minutes", "goalsPer90"),
#         ("Shots per 90 Minutes", "shotsPer90"),
#         ("Pass Success Rate (%)", "passSuccessRate")
#     ]
    
#     for metric_name, metric_key in metrics:
#         output.append(f"**{metric_name}**")
#         output.append("| Season | Value |")
#         output.append("|--------|--------|")
#         for stat in data['performanceMetrics'][metric_key]:
#             output.append(f"| {stat['season']} | {stat['value']} |")
#         output.append("")

#     return "\n".join(output)

# src/data/groq_client.py
from groq import Groq
import json

class SportsDataClient:
    def __init__(self):
        self.client = Groq(api_key="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")
        self.model = "llama3-70b-8192"

    def fetch_player_data(self, player_name):
        messages = [
            {
                "role": "system",
                "content": """You are a sports data analyst with access to current market values and statistics. 
                Return accurate player data in JSON format with the following structure:
                {
                    "player": {
                        "name": string,
                        "position": string,
                        "nationality": string,
                        "dateOfBirth": string,
                        "height": number,
                        "weight": number,
                        "currentTeam": string
                    },
                    "marketValue": {
                        "current": number,
                        "history": [
                            {
                                "date": string,
                                "value": number
                            }
                        ]
                    },
                    "transferHistory": [
                        {
                            "date": string,
                            "from": string,
                            "to": string,
                            "fee": number
                        }
                    ],
                    "performanceMetrics": {
                        "currentSeason": {
                            "appearances": number,
                            "goals": number,
                            "assists": number,
                            "minutesPlayed": number
                        },
                        "goalsPer90": [
                            {
                                "season": string,
                                "value": number
                            }
                        ],
                        "shotsPer90": [
                            {
                                "season": string,
                                "value": number
                            }
                        ],
                        "passSuccessRate": [
                            {
                                "season": string,
                                "value": number
                            }
                        ]
                    }
                }"""
            },
            {
                "role": "user",
                "content": f"Get detailed stats and current market value data for {player_name} in JSON format, including current 2023-2024 season data."
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

def format_player_data(data):
    output = []
    
    # Player Profile
    output.append("## Player Profile")
    player = data["player"]
    output.append(f"**Name:** {player['name']}")
    output.append(f"**Position:** {player['position']}")
    output.append(f"**Nationality:** {player['nationality']}")
    output.append(f"**Date of Birth:** {player['dateOfBirth']}")
    output.append(f"**Height:** {player['height']} cm")
    output.append(f"**Weight:** {player['weight']} kg")
    output.append(f"**Current Team:** {player['currentTeam']}\n")

    # Market Value
    output.append("## Market Value")
    output.append(f"**Current Value:** €{data['marketValue']['current']:,}")
    output.append("\n**Historical Values:**")
    for value in data['marketValue']['history']:
        output.append(f"- {value['date']}: €{value['value']:,}")
    output.append("")

    # Transfer History
    output.append("## Transfer History")
    for i, transfer in enumerate(data['transferHistory'], 1):
        output.append(f"{i}. **{transfer['to']}** ({transfer['date']})")
        output.append(f"   - From: {transfer['from']}")
        output.append(f"   - Fee: €{transfer['fee']:,}\n")

    # Current Season Performance
    output.append("## 2023-2024 Season Statistics")
    current = data['performanceMetrics']['currentSeason']
    output.append("| Statistic | Value |")
    output.append("|-----------|--------|")
    output.append(f"| Appearances | {current['appearances']} |")
    output.append(f"| Goals | {current['goals']} |")
    output.append(f"| Assists | {current['assists']} |")
    output.append(f"| Minutes Played | {current['minutesPlayed']} |\n")

    # Historical Performance Metrics
    output.append("## Performance Metrics\n")
    metrics = [
        ("Goals per 90 Minutes", "goalsPer90"),
        ("Shots per 90 Minutes", "shotsPer90"),
        ("Pass Success Rate (%)", "passSuccessRate")
    ]
    
    for metric_name, metric_key in metrics:
        output.append(f"**{metric_name}**")
        output.append("| Season | Value |")
        output.append("|--------|--------|")
        for stat in data['performanceMetrics'][metric_key]:
            output.append(f"| {stat['season']} | {stat['value']} |")
        output.append("")

    return "\n".join(output)
