import json
import os
from openai import OpenAI
#Tools and pydantic models to map dynamically
from tools import search_labor_code, search_tables_irs, search_social_security
from tools import SearchACT, SearchIRS, SearchSegSocial

class LaborLawAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        self.history = [
            {"role": "system", "content": (
                "You are an expert in Portuguese labor law. ALWAYS interact with the user in Portuguese (pt-PT)."
                "Rules: "
                "1.Strict grounding: NEVER answer without using tools to consult the sources. "
                "2.ALWAYS cite the URL returned by the tool. "
                "3.If the user doesn't give the salary or civil status for IRS calculations, ASK before searching[cite article 43]. "
                "4.If the law is unclear, refuse politely. Say that the legal risk is high[cite articles 17, 43]."
            )}
        ]
        #Mapped the name string to the respective function
        self.tool_map = {
            "search_labor_code": search_labor_code,
            "search_tables_irs": search_tables_irs,
            "search_social_security": search_social_security
        }

    def get_tools_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_labor_code",
                    "description": "Search the Labor Code. Use for vacations, dismissals, contracts.",
                    "parameters": SearchACT.model_json_schema()
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_tables_irs",
                    "description": "Search IRS tables. Use for withholding tax calculations. Requires brute salary and civil status.",
                    "parameters": SearchIRS.model_json_schema()
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_social_security",
                    "description": "Search Social Security. Use for taxes and contributions. Requires contract type.",
                    "parameters": SearchSegSocial.model_json_schema()
                }
            }
        ]

    def chat(self, user_msg: str) -> str:
        self.history.append({"role": "user", "content": user_msg})
        
        request_params = {
            "model": self.model,
            "messages": self.history,
            "temperature": 0.1, #Low temperature to stick to retrieved facts
            "tools": self.get_tools_schema()
        }
            
        response = self.client.chat.completions.create(**request_params)
        msg = response.choices[0].message
        
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            self.history.append(msg)
            
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if func_name in self.tool_map:
                    search_results = self.tool_map[func_name](**args)
                else:
                    search_results = "Tool not found."
                    
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": search_results
                })
                
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                temperature=0.1  #Keep it low for the final synthesis too
            )
            final_content = final_response.choices[0].message.content
            self.history.append({"role": "assistant", "content": final_content})
            return final_content
            
        else:
            self.history.append({"role": "assistant", "content": msg.content})
            return msg.content