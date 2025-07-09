# app/agents.py
import os
import requests
import json
import traceback
import time
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# --- Agent 1: The Research Analyst ---

def run_research_agent(company_name: str, company_url: str, pitch_deck_content: str = "", internal_notes: str = "") -> dict:
    """
    Performs deep research using an external AI and returns a structured JSON object.
    """
    print("🤖 AGENT 1: RESEARCH ANALYST STARTED")
    print("="*60)
    
    # Check environment variables first
    api_key = os.getenv("AI_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
    api_endpoint = os.getenv("AI_API_ENDPOINT") or "https://api.perplexity.ai/chat/completions"
    
    print(f"🔧 Environment Configuration:")
    print(f"   - AI_API_KEY: {'Found' if os.getenv('AI_API_KEY') else 'Not found'}")
    print(f"   - PERPLEXITY_API_KEY: {'Found' if os.getenv('PERPLEXITY_API_KEY') else 'Not found'}")
    print(f"   - AI_API_ENDPOINT: {api_endpoint}")
    print(f"   - Using API key: {'Found' if api_key else 'Not found'}")
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("⚠️ Warning: AI_API_KEY/PERPLEXITY_API_KEY not configured. Using mock data.")
        return get_mock_intelligence_brief(company_name)
    
    print(f"✅ API configuration validated")
    print(f"🔑 API key length: {len(api_key)}")
    print(f"🌐 API endpoint: {api_endpoint}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # This is the master prompt for our research agent.
    # It instructs the AI to think deeply and structure its findings.
    additional_context = ""
    if pitch_deck_content:
        additional_context += f"\n\nADDITIONAL CONTEXT - PITCH DECK CONTENT:\n{pitch_deck_content}\n"
        print(f"📄 Added pitch deck content: {len(pitch_deck_content)} chars")
    if internal_notes:
        additional_context += f"\n\nADDITIONAL CONTEXT - INTERNAL NOTES:\n{internal_notes}\n"
        print(f"📝 Added internal notes: {len(internal_notes)} chars")
    
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

    print(f"📝 Research prompt created: {len(research_prompt)} characters")

    # Check if we're using Perplexity API (which has different model names)
    if "perplexity.ai" in api_endpoint:
        payload = {
            "model": "sonar-pro",  # Updated to current Perplexity model name
            "messages": [{"role": "user", "content": research_prompt}],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        print(f"🔧 Using Perplexity API format with model: sonar-pro")
    else:
        # Default to OpenAI format
        payload = {
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": research_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 4000
        }
        print(f"🔧 Using OpenAI API format with model: gpt-4-turbo")

    print(f"📊 Payload prepared:")
    print(f"   - Model: {payload['model']}")
    print(f"   - Temperature: {payload['temperature']}")
    print(f"   - Max tokens: {payload['max_tokens']}")
    print(f"   - Messages count: {len(payload['messages'])}")

    try:
        print(f"🌐 Making API request to: {api_endpoint}")
        start_time = time.time()
        
        response = requests.post(
            api_endpoint, 
            headers=headers, 
            json=payload, 
            timeout=180
        )
        
        request_time = round(time.time() - start_time, 2)
        print(f"⏰ API request completed in {request_time} seconds")
        print(f"📊 HTTP Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API Error - Status: {response.status_code}")
            print(f"❌ Response headers: {dict(response.headers)}")
            print(f"❌ Response text: {response.text}")
            
            if response.status_code == 400:
                print("❌ Bad Request - Check API key and model name")
            elif response.status_code == 401:
                print("❌ Unauthorized - API key is invalid")
            elif response.status_code == 429:
                print("❌ Rate Limited - Too many requests")
            elif response.status_code == 500:
                print("❌ Server Error - API service is down")
            
            print("🔄 Falling back to mock data due to API error")
            return get_mock_intelligence_brief(company_name)
        
        response.raise_for_status()
        
        try:
            result = response.json()
            print(f"✅ API response parsed successfully")
            print(f"📊 Response structure keys: {list(result.keys())}")
            
        except json.JSONDecodeError as json_error:
            print(f"❌ Failed to parse API response as JSON: {str(json_error)}")
            print(f"❌ Raw response: {response.text[:1000]}...")
            print("🔄 Falling back to mock data due to JSON parse error")
            return get_mock_intelligence_brief(company_name)
        
        # Extract content based on API format
        try:
            if "perplexity.ai" in api_endpoint:
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(f"✅ Extracted content from Perplexity response")
                else:
                    print(f"❌ Unexpected Perplexity response structure: {result}")
                    print("🔄 Falling back to mock data")
                    return get_mock_intelligence_brief(company_name)
            else:
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(f"✅ Extracted content from OpenAI response")
                else:
                    print(f"❌ Unexpected OpenAI response structure: {result}")
                    print("🔄 Falling back to mock data")
                    return get_mock_intelligence_brief(company_name)
            
            print(f"📄 Content extracted: {len(content)} characters")
            print(f"📄 Content preview: {content[:200]}...")
            
        except (KeyError, IndexError, TypeError) as extract_error:
            print(f"❌ Error extracting content from response: {str(extract_error)}")
            print(f"❌ Response structure: {result}")
            print("🔄 Falling back to mock data")
            return get_mock_intelligence_brief(company_name)
        
        # Parse the JSON response
        try:
            # Find JSON in the response (in case there's extra text)
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                print(f"❌ No JSON object found in response content")
                print(f"❌ Content: {content}")
                print("🔄 Falling back to mock data")
                return get_mock_intelligence_brief(company_name)
            
            json_str = content[start_idx:end_idx]
            print(f"📄 Extracted JSON string: {len(json_str)} characters")
            
            intelligence_brief = json.loads(json_str)
            
            # Validate the structure
            required_keys = ['companyName', 'tagline', 'executiveSummary']
            for key in required_keys:
                if key not in intelligence_brief:
                    print(f"⚠️ Warning: Missing required key '{key}' in AI response")
            
            print("✅ Successfully parsed AI response JSON")
            print(f"📊 Intelligence brief keys: {list(intelligence_brief.keys())}")
            print(f"📊 Company name from AI: {intelligence_brief.get('companyName', 'Not found')}")
            print("="*60)
            return intelligence_brief
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON from AI response: {str(e)}")
            print(f"❌ JSON string that failed: {json_str[:500]}...")
            print(f"❌ Raw content: {content}")
            print("🔄 Falling back to mock data due to JSON decode error")
            return get_mock_intelligence_brief(company_name)
            
    except requests.exceptions.Timeout as timeout_error:
        print(f"❌ API request timed out after 180 seconds: {str(timeout_error)}")
        print("🔄 Falling back to mock data due to timeout")
        return get_mock_intelligence_brief(company_name)
        
    except requests.exceptions.ConnectionError as conn_error:
        print(f"❌ Connection error: {str(conn_error)}")
        print("🔄 Falling back to mock data due to connection error")
        return get_mock_intelligence_brief(company_name)
        
    except requests.exceptions.RequestException as req_error:
        print(f"❌ Request error: {str(req_error)}")
        print(f"❌ Error type: {type(req_error)}")
        if hasattr(req_error, 'response') and req_error.response:
            print(f"❌ Status code: {req_error.response.status_code}")
            print(f"❌ Response text: {req_error.response.text}")
        print("🔄 Falling back to mock data due to request error")
        return get_mock_intelligence_brief(company_name)
        
    except Exception as e:
        print(f"❌ Unexpected error in research agent: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        print("🔄 Falling back to mock data due to unexpected error")
        return get_mock_intelligence_brief(company_name)


def get_mock_intelligence_brief(company_name: str) -> dict:
    """Return mock intelligence brief for testing when API is not available."""
    
    print(f"🎭 GENERATING MOCK DATA for {company_name}")
    
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
        "Slack": "Where work happens - transforming business communication",
        "VOICENX": "Revolutionizing voice technology for the next generation"
    }
    
    # Get company-specific tagline or create a generic one
    tagline = company_taglines.get(company_name, f"Leading innovation in their industry")
    
    mock_data = {
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
    
    print(f"✅ Mock data generated successfully for {company_name}")
    print(f"📊 Mock data keys: {list(mock_data.keys())}")
    
    return mock_data


# --- Agent 2: The Formatting Specialist ---

def run_formatting_agent(intelligence_brief: dict, report_type: str) -> str:
    """
    Populates a Markdown template with the provided JSON data. This agent is deterministic.
    """
    print(f"📝 AGENT 2: FORMATTING SPECIALIST STARTED")
    print(f"📄 Report type: {report_type}")
    print(f"📊 Intelligence brief keys: {list(intelligence_brief.keys())}")
    
    try:
        # Set up Jinja2 to load templates from the 'templates' directory
        template_dir = './app/templates/'
        print(f"📁 Loading templates from: {template_dir}")
        
        env = Environment(loader=FileSystemLoader(template_dir))

        # Add today's date to the intelligence brief
        intelligence_brief['today_date'] = datetime.now().strftime('%B %d, %Y')
        print(f"📅 Added today's date: {intelligence_brief['today_date']}")

        if report_type == 'one_pager':
            template_name = 'one_pager_template.md'
        elif report_type == 'deep_dive':
            template_name = 'deep_dive_template.md'
        else:
            raise ValueError(f"Invalid report type specified: {report_type}. Must be 'one_pager' or 'deep_dive'.")

        print(f"📄 Loading template: {template_name}")
        
        try:
            template = env.get_template(template_name)
            print(f"✅ Template loaded successfully")
        except Exception as template_error:
            print(f"❌ Failed to load template {template_name}: {str(template_error)}")
            raise

        # Render the template with the data from the intelligence brief
        print(f"🔄 Rendering template with intelligence brief...")
        try:
            formatted_markdown = template.render(intelligence_brief)
            print(f"✅ Template rendered successfully")
            print(f"📄 Output length: {len(formatted_markdown)} characters")
            return formatted_markdown
        except Exception as render_error:
            print(f"❌ Failed to render template: {str(render_error)}")
            print(f"❌ Render error traceback: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        print(f"❌ Error in formatting agent: {str(e)}")
        print(f"❌ Formatting agent traceback: {traceback.format_exc()}")
        raise 