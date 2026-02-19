# Ingestion Queue Review Guide

## Overview

You have **675 items** in the ingestion queue that need review. These items were automatically collected from your configured RSS feeds and need to be reviewed before they become incidents in the main database.

## Quick Start

1. **Access**: Navigate to http://192.168.0.18:30800/ingestion
2. **Login**: `admin@example.com` / `changeme123`
3. **Filter**: Use the status filter dropdown to focus on specific items
4. **Review**: Click "Review" on any item to see details and make decisions

## Review Workflow

### Step 1: Review Item Details

When you click "Review" on an item, you'll see:

- **Title & Author**: Automatically extracted from the source
- **Source URL**: Link to the original article (click to verify)
- **Content**: Full text of the article for your review
- **Metadata**: Publication date, source type, timestamps
- **Extracted Data**: Structured information pulled from the source

### Step 2: Make a Decision

You have 4 options for each item:

1. **✅ Approve** - Item is relevant and should become an incident
   - Creates an incident in the main database
   - Marks item as processed
   - Ready for public viewing

2. **❌ Reject** - Item is not relevant or doesn't meet criteria
   - Item is marked as rejected
   - Will not become an incident
   - Keeps queue clean

3. **✏️ Needs Edit** - Item has potential but needs modification
   - Marks for later manual editing
   - Use this for items that need:
     - Additional context
     - Fact-checking
     - Source verification
     - Category refinement

4. **🗑️ Delete** - Permanently remove the item
   - Use sparingly
   - Better to reject than delete (maintains audit trail)

## Review Strategies

### Strategy 1: Filter by Status (Recommended)

Start with the **Status Filter** dropdown:

1. **Focus on "Pending" first** - These need initial review
2. **Review "Needs Edit" second** - Items flagged for attention
3. **Audit "Approved"** - Double-check approved items
4. **Clean up "Rejected"** - Review rejected items periodically

### Strategy 2: Source-Based Review

Review by source type for consistency:

- **news_primary**: Major news outlets (ProPublica, The Intercept, BBC)
- **ngo_report**: NGO reports (EFF, ACLU)
- News sources tend to be more reliable and need less scrutiny

### Strategy 3: Batch Processing

Process similar items together:

1. **Sort by type/source** - Review similar content at once
2. **Use patterns** - Develop criteria for what to approve/reject
3. **Take breaks** - Review fatigue is real; process 20-50 items at a time

### Strategy 4: Priority-Based Review

Focus on high-impact items first:

1. **Recent items** - Current events (last 7-30 days)
2. **High-severity potential** - Constitutional violations, corruption
3. **Primary sources** - Direct reporting vs. aggregation
4. **Verified sources** - Established news organizations

## What to Look For

### ✅ Approve if the item:

- Reports on government misconduct or accountability issues
- Comes from a credible source
- Has sufficient detail and context
- Includes dates, locations, and specific individuals/agencies
- Relates to:
  - Constitutional violations
  - Corruption or abuse of power
  - Civil liberties abuses
  - Government transparency issues
  - Law enforcement misconduct
  - Surveillance overreach

### ❌ Reject if the item:

- Is duplicate content (same story from different sources)
- Lacks credibility or verification
- Is opinion/editorial without factual basis
- Is off-topic (not about government accountability)
- Is spam or low-quality content
- Lacks sufficient detail to be useful

### ✏️ Needs Edit if the item:

- Has good content but poor categorization
- Needs additional context or fact-checking
- Requires source verification
- Should be merged with another incident
- Needs severity classification adjustment

## Bulk Operations Tips

### Current System

- **No bulk actions yet** - Each item must be reviewed individually
- **Status filter** helps focus your review sessions
- **Pagination** shows 20 items at a time

### Recommended Workflow

1. **Session 1** (1-2 hours): Review 50-100 items
   - Filter: Status = "Pending"
   - Focus on most recent items first
   - Quick decisions on obvious approvals/rejections

2. **Session 2** (1 hour): Review "Needs Edit" items
   - These require more attention
   - Decide: Can it be approved now, or should it be rejected?

3. **Session 3** (30 mins): Quality check
   - Review recent approvals
   - Ensure consistency in your decisions

## Keyboard Efficiency

While the UI doesn't have built-in keyboard shortcuts, you can use browser features:

- **Ctrl/Cmd + Click** on "Review" to open in new tab
- **Ctrl/Cmd + W** to close tab after review
- **Alt + Left Arrow** to go back to queue
- Use browser's back button after each review

## Quality Control

### Self-Audit Checklist

After processing 50-100 items, review your decisions:

- [ ] Are my approval criteria consistent?
- [ ] Am I being too lenient or too strict?
- [ ] Are duplicate stories being caught?
- [ ] Is source credibility being considered?
- [ ] Are items properly categorized?

### Common Pitfalls

1. **Approval fatigue** - Don't approve everything just to clear the queue
2. **Over-rejection** - Don't reject marginal items; use "Needs Edit"
3. **Duplicate approvals** - Check if a similar story is already approved
4. **Ignoring source quality** - Credibility matters
5. **Speed over quality** - It's okay to take your time

## Current Sources

Your system is ingesting from these feeds:

1. **ProPublica** - Investigative journalism
2. **The Intercept** - National security and civil liberties
3. **BBC News** - International and domestic news
4. **Electronic Frontier Foundation (EFF)** - Digital rights and privacy
5. **NPR** - General news and investigations

These are all high-quality sources, so your approval rate should be relatively high (60-80%).

## Tracking Progress

### Daily Goals

- **Day 1**: Review 100 items (15% of queue)
- **Day 2-5**: Review 100 items per day
- **Day 6-7**: Review "Needs Edit" and quality check

At 100 items/day, you'll clear the queue in about 7 days with 1-2 hours per day.

### Progress Tracking

The queue page shows: `675 items awaiting review`

After each session, note your progress:
- Items reviewed: ___
- Approved: ___
- Rejected: ___
- Needs Edit: ___
- Remaining: ___

## Future Enhancements (Roadmap)

Consider requesting these features:

1. **Bulk actions** - Select multiple items for batch approve/reject
2. **Keyboard shortcuts** - Navigate and decide without mouse
3. **Smart filtering** - Filter by date range, source, keywords
4. **Duplicate detection** - Auto-flag potential duplicates
5. **Auto-categorization** - ML-suggested categories
6. **Review statistics** - Track your review patterns and speed

## Support

If you encounter issues:

1. **401 Errors**: Refresh the page and log in again (token expired)
2. **Missing items**: Check the status filter (might be filtered out)
3. **Can't approve**: Verify you have REVIEWER or higher role
4. **Performance issues**: Browser may need cache clear

## Tips for Success

1. **Set a timer** - Review for 25-30 minutes, then take a 5-minute break
2. **Stay consistent** - Develop clear criteria and stick to them
3. **Document decisions** - Keep notes on edge cases for future reference
4. **Ask for help** - If unsure about an item, mark "Needs Edit" and revisit later
5. **Celebrate progress** - Acknowledge when you hit milestones (100, 200, 500 items)

---

**Ready to start?** Log in and begin with the "Pending" filter. Good luck! 🚀
