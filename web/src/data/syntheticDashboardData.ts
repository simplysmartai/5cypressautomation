export const companyProfile = {
  name: 'Northstar Components',
  segment: 'B2B parts distributor',
  period: 'Jan 2025 - Jun 2026',
  note: 'Synthetic portfolio dataset. No client or confidential data is represented.',
};

export const monthlyPerformance = [
  { month: 'Jan 2025', revenue: 184000, pipeline: 412000, leads: 142, mqls: 47, dealsWon: 8, automationHours: 84 },
  { month: 'Feb 2025', revenue: 191000, pipeline: 438000, leads: 151, mqls: 52, dealsWon: 9, automationHours: 91 },
  { month: 'Mar 2025', revenue: 206000, pipeline: 461000, leads: 166, mqls: 57, dealsWon: 10, automationHours: 96 },
  { month: 'Apr 2025', revenue: 198000, pipeline: 455000, leads: 159, mqls: 54, dealsWon: 9, automationHours: 104 },
  { month: 'May 2025', revenue: 218000, pipeline: 489000, leads: 174, mqls: 61, dealsWon: 11, automationHours: 113 },
  { month: 'Jun 2025', revenue: 232000, pipeline: 502000, leads: 181, mqls: 66, dealsWon: 12, automationHours: 121 },
  { month: 'Jul 2025', revenue: 226000, pipeline: 497000, leads: 177, mqls: 62, dealsWon: 10, automationHours: 128 },
  { month: 'Aug 2025', revenue: 241000, pipeline: 536000, leads: 190, mqls: 71, dealsWon: 13, automationHours: 136 },
  { month: 'Sep 2025', revenue: 254000, pipeline: 562000, leads: 203, mqls: 76, dealsWon: 14, automationHours: 145 },
  { month: 'Oct 2025', revenue: 263000, pipeline: 581000, leads: 216, mqls: 81, dealsWon: 14, automationHours: 153 },
  { month: 'Nov 2025', revenue: 249000, pipeline: 548000, leads: 197, mqls: 72, dealsWon: 12, automationHours: 160 },
  { month: 'Dec 2025', revenue: 271000, pipeline: 604000, leads: 222, mqls: 84, dealsWon: 15, automationHours: 168 },
  { month: 'Jan 2026', revenue: 278000, pipeline: 632000, leads: 231, mqls: 89, dealsWon: 16, automationHours: 176 },
  { month: 'Feb 2026', revenue: 286000, pipeline: 654000, leads: 238, mqls: 91, dealsWon: 16, automationHours: 181 },
  { month: 'Mar 2026', revenue: 302000, pipeline: 681000, leads: 249, mqls: 97, dealsWon: 17, automationHours: 188 },
  { month: 'Apr 2026', revenue: 297000, pipeline: 674000, leads: 242, mqls: 94, dealsWon: 16, automationHours: 194 },
  { month: 'May 2026', revenue: 318000, pipeline: 712000, leads: 261, mqls: 103, dealsWon: 18, automationHours: 203 },
  { month: 'Jun 2026', revenue: 329000, pipeline: 746000, leads: 274, mqls: 109, dealsWon: 19, automationHours: 211 },
];

export const pipelineStages = [
  { stage: 'New', value: 118000, count: 31, probability: 0.12 },
  { stage: 'Qualified', value: 174000, count: 24, probability: 0.28 },
  { stage: 'Demo / Fit', value: 203000, count: 17, probability: 0.45 },
  { stage: 'Proposal', value: 161000, count: 9, probability: 0.62 },
  { stage: 'Commit', value: 90000, count: 4, probability: 0.82 },
];

export const campaignPerformance = [
  { channel: 'Organic Search', spend: 4200, leads: 94, revenue: 128000, conversionRate: 0.18 },
  { channel: 'LinkedIn', spend: 7600, leads: 61, revenue: 99000, conversionRate: 0.15 },
  { channel: 'Email Nurture', spend: 1800, leads: 49, revenue: 87000, conversionRate: 0.22 },
  { channel: 'Referral', spend: 900, leads: 36, revenue: 114000, conversionRate: 0.31 },
  { channel: 'Paid Search', spend: 6200, leads: 34, revenue: 52000, conversionRate: 0.11 },
];

export const invoiceAging = [
  { bucket: 'Current', amount: 148000, invoices: 42 },
  { bucket: '1-30', amount: 78000, invoices: 21 },
  { bucket: '31-60', amount: 41000, invoices: 12 },
  { bucket: '61-90', amount: 18000, invoices: 5 },
  { bucket: '90+', amount: 9000, invoices: 3 },
];

export const automationWorkflows = [
  { workflow: 'Lead intake routing', runs: 1324, successRate: 0.982, hoursSaved: 54, owner: 'Sales Ops' },
  { workflow: 'Invoice reminder cadence', runs: 486, successRate: 0.971, hoursSaved: 39, owner: 'Finance' },
  { workflow: 'Weekly KPI refresh', runs: 78, successRate: 0.987, hoursSaved: 44, owner: 'Leadership' },
  { workflow: 'Quote follow-up tasks', runs: 912, successRate: 0.964, hoursSaved: 33, owner: 'Sales' },
  { workflow: 'Support ticket tagging', runs: 1108, successRate: 0.956, hoursSaved: 41, owner: 'Success' },
];

export const accountHealth = [
  { account: 'Atlas Fabrication', segment: 'Enterprise', revenue: 92000, health: 91, renewal: 'Aug 2026', risk: 'Low' },
  { account: 'Brightline Medical', segment: 'Mid-market', revenue: 74000, health: 84, renewal: 'Sep 2026', risk: 'Low' },
  { account: 'Cobalt Systems', segment: 'Mid-market', revenue: 68000, health: 72, renewal: 'Jul 2026', risk: 'Medium' },
  { account: 'Keystone Labs', segment: 'SMB', revenue: 39000, health: 66, renewal: 'Jul 2026', risk: 'Medium' },
  { account: 'Summit Robotics', segment: 'Enterprise', revenue: 104000, health: 88, renewal: 'Oct 2026', risk: 'Low' },
];

const latest = monthlyPerformance[monthlyPerformance.length - 1];
const previous = monthlyPerformance[monthlyPerformance.length - 2];
const latestQuarter = monthlyPerformance.slice(-3);
const previousQuarter = monthlyPerformance.slice(-6, -3);

const sum = <T>(items: T[], selector: (item: T) => number) =>
  items.reduce((total, item) => total + selector(item), 0);

export const dashboardSummary = {
  revenue: latest.revenue,
  revenueChange:
    (sum(latestQuarter, (month) => month.revenue) - sum(previousQuarter, (month) => month.revenue)) /
    sum(previousQuarter, (month) => month.revenue),
  pipeline: latest.pipeline,
  leadConversion: latest.mqls / latest.leads,
  automationHours: latest.automationHours,
  automationChange: (latest.automationHours - previous.automationHours) / previous.automationHours,
  arOutstanding: sum(invoiceAging, (bucket) => bucket.amount),
  weightedPipeline: sum(pipelineStages, (stage) => stage.value * stage.probability),
};
