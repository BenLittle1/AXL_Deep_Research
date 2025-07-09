<div class="header">
  <h1>{{ companyName }}</h1>
  <p class="one-liner">{{ tagline }}</p>
</div>

## EXECUTIVE SUMMARY
{{ executiveSummary }}

## COMPANY OVERVIEW
**Founded:** {{ foundedYear }} | **Business Model:** {{ businessModel }} | **Target Market:** {{ marketAnalysis.targetCustomer }}

### Problem Statement
{{ problemStatement }}

### Solution
{{ solution }}

<div class="page-break"></div>

## FINANCIAL OVERVIEW
<div class="metrics-box">
  <div class="metric-row">
    <span class="metric-label">Total Funding Raised:</span>
    <span>{{ financials.totalFunding }}</span>
  </div>
  <div class="metric-row">
    <span class="metric-label">Current Revenue (ARR):</span>
    <span>{{ financials.revenue }}</span>
  </div>
  <div class="metric-row">
    <span class="metric-label">Valuation:</span>
    <span>{{ financials.valuation }}</span>
  </div>
  <div class="metric-row">
    <span class="metric-label">Employee Count:</span>
    <span>{{ team|length }}+ employees</span>
  </div>
</div>

### Funding History
{% if financials.fundingRounds %}
| Round | Amount | Date | Lead Investor |
|:------|:-------|:-----|:--------------|
{% for round in financials.fundingRounds %}
| {{ round.type }} | {{ round.amount }} | {{ round.date }} | {{ round.leadInvestor }} |
{% endfor %}
{% else %}
Funding information not publicly available.
{% endif %}

## MARKET ANALYSIS
### Market Size and Opportunity
**TAM:** {{ marketAnalysis.sizeTAM }} | **SAM:** {{ marketAnalysis.sizeSAM }} | **SOM:** {{ marketAnalysis.sizeSOM }}

### Key Market Trends
{% for trend in marketAnalysis.keyTrends %}
• {{ trend }}
{% endfor %}

### Competitive Landscape
{% if marketAnalysis.competitors %}
**Primary Competitors:**
{% for competitor in marketAnalysis.competitors %}
• **{{ competitor.name }}** - {{ competitor.description }}
{% endfor %}
{% else %}
Detailed competitive analysis requires further research.
{% endif %}

<div class="page-break"></div>

## LEADERSHIP TEAM
{% for member in team %}
### {{ member.name }} - {{ member.title }}
{{ member.background }}
{% endfor %}

## TECHNOLOGY & PRODUCT
### Product Overview
{{ productOverview }}

### Technology Stack
{% if technologyStack %}
{% for tech in technologyStack %}
• {{ tech }}
{% endfor %}
{% else %}
Technology stack details require further investigation.
{% endif %}

### Intellectual Property
{% if intellectualProperty %}
{% for ip in intellectualProperty %}
• {{ ip }}
{% endfor %}
{% else %}
Intellectual property portfolio under review.
{% endif %}

<div class="page-break"></div>

## STRATEGIC ASSESSMENT
<div class="two-column">
  <div class="column">
    <div class="analysis-box">
      <div class="analysis-header">Strengths</div>
      {% for strength in swotAnalysis.strengths %}
      • {{ strength }}
      {% endfor %}
    </div>
    
    <div class="analysis-box">
      <div class="analysis-header">Opportunities</div>
      {% for opportunity in swotAnalysis.opportunities %}
      • {{ opportunity }}
      {% endfor %}
    </div>
  </div>
  
  <div class="column">
    <div class="analysis-box">
      <div class="analysis-header">Weaknesses</div>
      {% for weakness in swotAnalysis.weaknesses %}
      • {{ weakness }}
      {% endfor %}
    </div>
    
    <div class="analysis-box">
      <div class="analysis-header">Threats</div>
      {% for threat in swotAnalysis.threats %}
      • {{ threat }}
      {% endfor %}
    </div>
  </div>
</div>

## INVESTMENT CONSIDERATIONS
### Key Investment Strengths
{% for strength in swotAnalysis.strengths[:3] %}
• {{ strength }}
{% endfor %}

### Risk Factors
{% for weakness in swotAnalysis.weaknesses %}
• {{ weakness }}
{% endfor %}

### Growth Opportunities
{% for opportunity in swotAnalysis.opportunities %}
• {{ opportunity }}
{% endfor %}

## RECOMMENDATION
Based on this analysis, {{ companyName }} presents {{ "significant potential" if financials.totalFunding else "early-stage opportunity" }} in the {{ marketAnalysis.targetCustomer }} market. Key factors supporting this assessment include their {{ swotAnalysis.strengths[0] if swotAnalysis.strengths else "strong market position" }} and {{ marketAnalysis.keyTrends[0] if marketAnalysis.keyTrends else "favorable market conditions" }}. 