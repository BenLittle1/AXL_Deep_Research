<div class="header">
  <h1>{{ companyName }}</h1>
</div>

## EXECUTIVE SUMMARY
{{ executiveSummary }}

## KEY METRICS
<div class="metrics-box">
  <div class="metric-row">
    <span class="metric-label">Market Size (TAM):</span>
    <span>{{ marketAnalysis.sizeTAM }}</span>
  </div>
  <div class="metric-row">
    <span class="metric-label">Total Funding:</span>
    <span>{{ financials.totalFunding }}</span>
  </div>
  <div class="metric-row">
    <span class="metric-label">Current Revenue:</span>
    <span>{{ financials.revenue }}</span>
  </div>
  <div class="metric-row">
    <span class="metric-label">Founded:</span>
    <span>{{ foundedYear }}</span>
  </div>
</div>

## BUSINESS OVERVIEW
| **Problem Statement** | **Solution** |
|:----------------------|:-------------|
| {{ problemStatement }} | {{ solution }} |

**Business Model:** {{ businessModel }}

**Target Customer:** {{ marketAnalysis.targetCustomer }}

## LEADERSHIP TEAM
{% for member in team %}
**{{ member.name }}** - {{ member.title }} | {{ member.background }}
{% endfor %}

## MARKET POSITION
**Key Market Trends:** {% for trend in marketAnalysis.keyTrends %}{{ trend }}{% if not loop.last %} • {% endif %}{% endfor %}

## STRATEGIC ASSESSMENT
**Strengths:** {% for strength in swotAnalysis.strengths %}{{ strength }}{% if not loop.last %}, {% endif %}{% endfor %}

**Key Opportunities:** {% for opportunity in swotAnalysis.opportunities %}{{ opportunity }}{% if not loop.last %}, {% endif %}{% endfor %} 