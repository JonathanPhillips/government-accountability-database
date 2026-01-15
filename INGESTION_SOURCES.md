# Recommended Ingestion Sources for Government Accountability

## Government Watchdog Organizations

### **High Priority - NGO Reports**

1. **Project On Government Oversight (POGO)**
   - RSS: https://www.pogo.org/feeds/investigations
   - Type: `ngo_report`
   - Focus: Federal oversight, contractor accountability

2. **Government Accountability Project**
   - RSS: https://whistleblower.org/feed/
   - Type: `ngo_report`
   - Focus: Whistleblower protections, government transparency

3. **Center for Responsive Politics (OpenSecrets)**
   - RSS: https://www.opensecrets.org/news/rss
   - Type: `ngo_report`
   - Focus: Money in politics, lobbying

4. **Sunlight Foundation** (if active)
   - Type: `ngo_report`
   - Focus: Government transparency

### **Civil Liberties & Rights**

5. **ACLU** (currently has parsing issues)
   - RSS: https://www.aclu.org/news/feed
   - Type: `ngo_report`
   - Focus: Civil liberties, government overreach

6. **Electronic Frontier Foundation**
   - RSS: https://www.eff.org/rss/updates.xml
   - Type: `ngo_report`
   - Focus: Digital rights, surveillance

7. **Human Rights Watch - USA**
   - RSS: https://www.hrw.org/rss
   - Type: `ngo_report`
   - Focus: Human rights violations

### **Investigative Journalism**

8. **ProPublica**
   - RSS: https://www.propublica.org/feeds/propublica/main
   - Type: `news_primary`
   - Focus: Investigative reporting on government

9. **The Intercept**
   - RSS: https://theintercept.com/feed/
   - Type: `news_primary`
   - Focus: National security, surveillance

10. **Center for Public Integrity**
    - RSS: https://publicintegrity.org/feed/
    - Type: `news_primary`
    - Focus: Government corruption, lobbying

### **Government Official Sources**

11. **USA.gov News**
    - RSS: https://www.usa.gov/rss/updates.xml
    - Type: `government_report`
    - Focus: Official government announcements

12. **GAO Reports** (Government Accountability Office)
    - Check: https://www.gao.gov/rss-feeds
    - Type: `government_report`
    - Focus: Official audit reports

13. **Inspector General Reports**
    - Various IG RSS feeds by agency
    - Type: `government_report`
    - Focus: Internal oversight

### **Court & Legal Sources**

14. **PACER (Public Access to Court Electronic Records)**
    - API/RSS if available
    - Type: `court_filing`
    - Focus: Federal court filings

15. **Supreme Court**
    - RSS: https://www.supremecourt.gov/rss/cases.xml
    - Type: `court_filing`
    - Focus: Supreme Court decisions

### **FOIA & Transparency**

16. **MuckRock**
    - RSS: https://www.muckrock.com/feeds/
    - Type: `foia`
    - Focus: FOIA requests and responses

17. **DocumentCloud**
    - API access
    - Type: `leaked_document` / `foia`
    - Focus: Document repository

## Testing Sources

### **Currently Configured**
- BBC News (working) - `news_primary`
- NPR News - `news_primary`
- EFF Updates - `ngo_report`

### **Recommended Next Steps**

1. Test ProPublica feed first (reliable, government-focused)
2. Add POGO investigations feed
3. Add OpenSecrets for money in politics
4. Add The Intercept for national security
5. Test GAO reports feed

## Source Priority Levels

**Tier 1 (Essential)**:
- ProPublica
- POGO
- OpenSecrets
- GAO Reports

**Tier 2 (Important)**:
- EFF
- The Intercept
- Center for Public Integrity
- MuckRock

**Tier 3 (Supplementary)**:
- BBC/NPR News
- Human Rights Watch
- Government Accountability Project
- ACLU (when feed is fixed)

## Notes

- Check each RSS feed validity before adding
- Some feeds may require XML parsing fixes
- Court filings may need PACER access
- PDF ingestion works for government reports
- YouTube ingestion works for hearings/testimony
