# app/agents.py
import os
import requests
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# --- Agent 1: The Research Analyst ---

def run_research_agent(company_name: str, company_url: str, pitch_deck_content: str = "", internal_notes: str = "") -> dict:
    """
    Performs deep research using an external AI and returns a structured JSON object.
    """
    api_key = os.getenv("AI_API_KEY")
    api_endpoint = os.getenv("AI_API_ENDPOINT")
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Warning: AI_API_KEY not configured. Using mock data.")
        return get_mock_intelligence_brief(company_name)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # This is the master prompt for our research agent.
    # It instructs the AI to think deeply and structure its findings.
    additional_context = ""
    if pitch_deck_content:
        additional_context += f"\n\nADDITIONAL CONTEXT - PITCH DECK CONTENT:\n{pitch_deck_content}\n"
    if internal_notes:
        additional_context += f"\n\nADDITIONAL CONTEXT - INTERNAL NOTES:\n{internal_notes}\n"
    
    research_prompt = f"""
    You are a world-class Tier 1 financial and market research analyst.
    Your sole task is to conduct a deep, multi-source investigation of the company '{company_name}' (website: {company_url}).
    You must investigate their business model, market positioning, financials, team, technology, and competitive landscape.
    {additional_context}
    Use any provided pitch deck content and internal notes to enhance your research and provide more accurate, detailed insights.
    Cross-reference the provided materials with your external research to create the most comprehensive analysis possible.
    Synthesize all of your findings into a single, structured JSON object. Do not write any prose or explanations outside of the JSON.
    The JSON object must strictly adhere to the following schema. If you cannot find information for a field, you MUST return an empty string "" or an empty array [].

    JSON SCHEMA:
    {{
      "companyName": "string",
      "foundedYear": "string (Year)",
      "tagline": "string",
      "executiveSummary": "A concise 3-4 sentence summary of the entire business.",
      "problemStatement": "A clear, detailed description of the customer problem they solve.",
      "solution": "A detailed description of their product or service and how it solves the problem.",
      "businessModel": "How the company generates revenue (e.g., SaaS tiers, transaction fees, etc.).",
      "marketAnalysis": {{
        "sizeTAM": "string (Total Addressable Market size, e.g., '$150B')",
        "sizeSAM": "string (Serviceable Addressable Market size, e.g., '$15B')",
        "sizeSOM": "string (Serviceable Obtainable Market size, e.g., '$1.5B')",
        "keyTrends": ["List of key market trends benefiting the company."],
        "targetCustomer": "A description of the ideal customer profile.",
        "competitors": [
          {{
            "name": "string",
            "description": "string"
          }}
        ]
      }},
      "team": [
        {{
          "name": "string",
          "title": "string",
          "background": "A summary of their relevant experience."
        }}
      ],
      "financials": {{
        "totalFunding": "string",
        "lastRound": "string (e.g., 'Series A, $6.5M, led by Capital Ventures')",
        "revenue": "string (e.g., '$1.2M ARR')",
        "valuation": "string (e.g., '$50M')",
        "fundingRounds": [
          {{
            "type": "string",
            "amount": "string",
            "date": "string",
            "leadInvestor": "string"
          }}
        ]
      }},
      "productOverview": "string",
      "technologyStack": ["List of technologies used"],
      "intellectualProperty": ["List of patents, trademarks, etc."],
      "swotAnalysis": {{
        "strengths": ["List of internal strengths."],
        "weaknesses": ["List of internal weaknesses."],
        "opportunities": ["List of external market opportunities."],
        "threats": ["List of external market threats."]
      }}
    }}
    
    Respond ONLY with the JSON object. No additional text.
    """

    # Check if we're using Perplexity API (which has different model names)
    if "perplexity.ai" in api_endpoint:
        payload = {
            "model": "sonar-pro",  # Updated to current Perplexity model name
            "messages": [{"role": "user", "content": research_prompt}],
            "temperature": 0.1,
            "max_tokens": 4000
        }
    else:
        # Default to OpenAI format
        payload = {
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": research_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 4000
        }

    try:
        print(f"Calling AI API: {api_endpoint}")
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract content based on API format
        if "perplexity.ai" in api_endpoint:
            content = result["choices"][0]["message"]["content"]
        else:
            content = result["choices"][0]["message"]["content"]
        
        # Parse the JSON response
        try:
            # Find JSON in the response (in case there's extra text)
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                intelligence_brief = json.loads(json_str)
                print("Successfully parsed AI response JSON")
                return intelligence_brief
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from AI response: {e}")
            print(f"Raw content: {content}")
            return get_mock_intelligence_brief(company_name)
            
    except requests.exceptions.RequestException as e:
        print(f"Perplexity API error: {response.status_code} - {response.text}")
        return get_mock_intelligence_brief(company_name)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return get_mock_intelligence_brief(company_name)


def get_mock_intelligence_brief(company_name: str) -> dict:
    """Return mock intelligence brief for testing when API is not available."""
    
    # Company-specific taglines based on company name
    company_taglines = {
        "Tesla": "Accelerating the world's transition to sustainable energy",
        "Microsoft": "Empowering every person and organization on the planet to achieve more", 
        "OpenAI": "Creating safe artificial general intelligence that benefits all of humanity",
        "SpaceX": "Making life multiplanetary through advanced space technology",
        "Airbnb": "Belong anywhere - connecting people through unique travel experiences",
        "Zoom": "Bringing the world together through frictionless video communications",
        "Stripe": "Increasing the GDP of the internet through payment infrastructure",
        "Netflix": "Entertainment that moves you - streaming content worldwide",
        "Shopify": "Making commerce better for everyone through e-commerce solutions",
        "Slack": "Where work happens - transforming business communication"
    }
    
    # Get company-specific tagline or create a generic one
    tagline = company_taglines.get(company_name, f"Leading innovation in their industry")
    
    return {
        "companyName": company_name,
        "foundedYear": "2019",
        "tagline": tagline,
        "executiveSummary": f"{company_name} is a fast-growing technology company that has shown strong market traction and innovation in their sector. The company has built a scalable platform that serves enterprise clients with proven customer adoption and revenue growth. Their strategic positioning in the market demonstrates significant potential for continued expansion and value creation.",
        "problemStatement": "Organizations face complex operational challenges that require innovative technology solutions. Traditional approaches are often inefficient, costly, and lack the scalability needed for modern business requirements.",
        "solution": f"{company_name} provides an advanced platform that addresses these challenges through innovative technology and user-centric design. The solution integrates seamlessly with existing systems while delivering measurable improvements in efficiency and outcomes.",
        "businessModel": "Multi-tier subscription model with enterprise-focused pricing. Revenue streams include core platform subscriptions, professional services, and premium feature add-ons.",
        "marketAnalysis": {
            "sizeTAM": "$85B",
            "sizeSAM": "$8.5B", 
            "sizeSOM": "$850M",
            "keyTrends": [
                "Digital transformation acceleration across industries",
                "Increased demand for scalable technology solutions",
                "Growing emphasis on operational efficiency and automation"
            ],
            "targetCustomer": "Mid-market to enterprise companies seeking innovative solutions to improve operational efficiency and business outcomes.",
            "competitors": [
                {
                    "name": "Industry Leader A",
                    "description": "Established player with traditional approach"
                },
                {
                    "name": "Emerging Competitor B", 
                    "description": "New entrant with focus on specific market segment"
                }
            ]
        },
        "team": [
            {
                "name": "Sarah Chen",
                "title": "CEO & Co-Founder",
                "background": "Former executive at leading technology company, MBA from top business school, 15+ years experience"
            },
            {
                "name": "Michael Rodriguez",
                "title": "CTO & Co-Founder", 
                "background": "Ex-senior engineer at major tech firm, advanced degree in computer science, expert in scalable systems"
            },
            {
                "name": "Jennifer Park",
                "title": "VP of Business Development",
                "background": "Former sales leader at enterprise software company, proven track record with Fortune 500 clients"
            }
        ],
        "financials": {
            "totalFunding": "$25.5M",
            "lastRound": "Series B, $18M, led by leading venture capital firm",
            "revenue": "$5.2M ARR",
            "valuation": "$120M",
            "fundingRounds": [
                {
                    "type": "Seed",
                    "amount": "$2.5M",
                    "date": "2020",
                    "leadInvestor": "Seed Capital Partners"
                },
                {
                    "type": "Series A",
                    "amount": "$5M", 
                    "date": "2021",
                    "leadInvestor": "Growth Ventures"
                },
                {
                    "type": "Series B",
                    "amount": "$18M",
                    "date": "2023", 
                    "leadInvestor": "Premier VC Fund"
                }
            ]
        },
        "productOverview": f"{company_name} offers a comprehensive platform designed for enterprise-scale operations with focus on user experience and measurable business impact.",
        "technologyStack": [
            "Cloud-native architecture",
            "Modern web frameworks", 
            "Scalable data processing",
            "Enterprise security standards"
        ],
        "intellectualProperty": [
            "Core platform patents pending",
            "Proprietary algorithms for optimization",
            "Trademark protection for brand assets"
        ],
        "swotAnalysis": {
            "strengths": [
                "Strong technical team with proven expertise",
                "High customer satisfaction and retention rates",
                "Proven product-market fit with measurable results",
                "Scalable business model with recurring revenue"
            ],
            "weaknesses": [
                "Limited brand recognition in competitive market",
                "Dependency on key founding team members",
                "Early stage international market presence"
            ],
            "opportunities": [
                "Large addressable market with significant growth potential",
                "Opportunity for strategic partnerships and integrations",
                "Expansion into adjacent market segments",
                "International market expansion possibilities"
            ],
            "threats": [
                "Competition from well-funded industry incumbents",
                "Economic uncertainty affecting enterprise spending",
                "Rapid technological change requiring continuous innovation",
                "Potential regulatory changes impacting business model"
            ]
        }
    }


# --- Agent 2: The Formatting Specialist ---

def run_formatting_agent(intelligence_brief: dict, report_type: str) -> str:
    """
    Populates a Markdown template with the provided JSON data. This agent is deterministic.
    """
    # Set up Jinja2 to load templates from the 'templates' directory
    env = Environment(loader=FileSystemLoader('./app/templates/'))

    # Add today's date to the intelligence brief
    intelligence_brief['today_date'] = datetime.now().strftime('%B %d, %Y')

    if report_type == 'one_pager':
        template = env.get_template('one_pager_template.md')
    elif report_type == 'deep_dive':
        template = env.get_template('deep_dive_template.md')
    else:
        raise ValueError("Invalid report type specified. Must be 'one_pager' or 'deep_dive'.")

    # Render the template with the data from the intelligence brief
    formatted_markdown = template.render(intelligence_brief)
    return formatted_markdown 