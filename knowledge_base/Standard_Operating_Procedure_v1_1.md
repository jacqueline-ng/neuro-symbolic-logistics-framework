# DataCo Standard Operating Procedure (SOP) v1.1
## Late Delivery Assessment and Response

### 1. Purpose
This Standard Operating Procedure (SOP) defines DataCo’s standardized process for assessing and responding to late or potentially late customer deliveries.

The SOP ensures that all delivery issues are handled in a manner that is:
* Operationally feasible,
* Financially responsible,
* Aligned with customer impact, and
* Supported by clear decision rationale and escalation controls.

---

### 2. Scope
This SOP applies to all customer orders managed by DataCo that are subject to delivery scheduling, fulfillment, and performance monitoring.

It supports both automated decision support systems and human-in-the-loop resolution where required.

---

### 3. Inputs
Late delivery assessment is performed using operational information and diagnostic archetypes from the following areas:
* **Execution Archetype:** Shipping service commitments and actual performance metrics.
* **Planning Archetype:** Real-time alignment between scheduled and real delivery durations.
* **Administrative Archetype:** Transaction types and payment verification characteristics (e.g., `Type_TRANSFER`).
* **Product/Financial Archetype:** Product-specific constraints and profitability indicators (e.g., `Order Item Id`).
* **Temporal/Operational Archetype:** Time-sensitive variables and warehouse processing schedules (e.g., `ship_hour`).
* **Geographic Context:** Regional delivery limitations and market-specific customs constraints.

---

### 4. Definitions
* **Shipping Delay:** The difference between actual delivery duration and the originally scheduled delivery duration:
  * *Negative value:* early delivery
  * *Zero:* on-time delivery
  * *Positive value:* late delivery
* **Mitigation Action:** Any operational or customer-facing action intended to reduce the impact of a delivery delay, including shipping adjustments, operational intervention, or controlled compensation.
* **Escalation:** Referral of a delivery case to a human decision-maker when automated resolution is restricted, infeasible, or requires management approval.

---

### 5. Late Delivery Decision Procedure

#### Step 1: Validate Order Eligibility
* **Objective:** Confirm whether the order qualifies for late delivery evaluation.
* **Assessment Criteria:**
  * Order status
  * Delivery status
  * Late delivery risk indicator
* **Procedure:**
  1. Orders that are canceled, closed, or fully completed are excluded from further processing.
  2. Orders with no identified risk of lateness require no action.
  3. Orders pending fulfillment, in transit, or flagged as at risk proceed to delivery performance assessment.

#### Step 2: Assess Shipping Commitment and Performance
* **Objective:** Determine whether delivery performance deviates from the committed timeline.
* **Assessment Criteria:**
  * Shipping service level
  * Scheduled delivery duration
  * Actual delivery duration
  * Calculated delivery delay
* **Procedure:**
  1. Orders are classified as early, on-time, or late based on delivery delay.
  2. Late deliveries are flagged for further evaluation.
  3. Orders meeting delivery commitments terminate with a no-action outcome.
* **Operational Constraints:**
  * Shipping services cannot be upgraded beyond the fastest available delivery option.
  * Expedited shipping cannot recover time lost due to upstream processing delays or congestion.
  * Certain shipping services restrict rerouting once dispatch has occurred.

#### Step 3: Evaluate Product and Handling Restrictions
* **Objective:** Identify physical or handling limitations that may affect resolution options.
* **Assessment Criteria:**
  * Product category
  * Handling department
  * Order quantity
* **Procedure:**
  1. Product characteristics or high-volume orders may restrict available mitigation actions.
  2. When handling restrictions apply, only permissible actions may be considered.
  3. Orders subject to such restrictions may require escalation rather than automated mitigation.
* **Operational Constraints:**
  * Bulk or high-quantity shipments cannot be expedited in the same manner as single-item deliveries.
  * Certain product categories impose handling requirements that limit rerouting or consolidation.

#### Step 4: Apply Financial Safeguards
* **Objective:** Ensure proposed resolution actions remain economically viable.
* **Assessment Criteria:**
  * Profit contribution of the order
  * Existing discounts or concessions
  * Customer revenue value
* **Procedure:**
  1. Orders with existing discounts may be restricted from additional compensation.
  2. Cost-incurring mitigation actions are evaluated against profitability indicators.
  3. Financially constrained cases may require escalation for management review.

#### Step 5: Consider Customer and Transaction Context
* **Objective:** Adjust handling strategy based on customer importance and transaction characteristics.
* **Assessment Criteria:**
  * Customer segment
  * Transaction or payment type
* **Procedure:**
  1. Certain customer segments may be prioritized for resolution within policy limits.
  2. Transactions requiring payment verification or administrative clearance may restrict available actions.

#### Step 6: Apply Geographic and Regional Limitations
* **Objective:** Account for location-based restrictions that override operational optimization.
* **Assessment Criteria:**
  * Market
  * Delivery region
  * Origin and destination country
* **Procedure:**
  1. International or region-specific deliveries may be subject to customs, regulatory, or infrastructure constraints.
  2. Geographic conditions may limit shipping adjustments or rerouting.
  3. Orders subject to non-negotiable geographic limitations follow alternate handling or escalation paths.
* **Operational Constraints:**
  * Customs clearance processes cannot be bypassed through shipping acceleration.
  * Regional infrastructure limitations may restrict mitigation options.
  * Geographic constraints take precedence over optimization and customer prioritization considerations.

#### Step 7: Resolution Selection and Escalation
* **Objective:** Select the most appropriate resolution based on all evaluated factors.

##### Step 7.1 Resolution Outcome Options
The following resolution outcomes may be applied:
* No action required
* Customer notification only
* Mitigation action
* Escalation to human operator

*Operational thresholds and cost limits governing these outcomes are configured outside this SOP.*

##### Step 7.2 Root-Cause-Aligned Resolution Selection
* **Objective:** Ensure that the selected resolution directly addresses the underlying cause of the delivery delay as identified by SHAP explainability.
* **Procedure:**
  1. The primary contributing cause of the delay is identified using diagnostic analysis (Local SHAP value).
  2. The Planner Agent maps the identified cause to one of the Six Core Archetypes.
  3. Resolution actions are selected based on the specific guidance provided below, ensuring compliance with operational constraints and financial safeguards.

**Resolution Guidance Table**

| Identified Diagnostic Cause | Strategic Resolution Path |
| :--- | :--- |
| **Execution-Related Delays** | Operational intervention or shipping adjustments may be considered where feasible (Reference Step 2). |
| **Planning-Related Delays** | Customer notification, expectation management, or delivery re-commitment is preferred (Reference Step 2). |
| **Administrative/Payment Delays** | Shipping upgrades are marked as logically inappropriate. Resolution must focus on administrative clearance or escalation (Reference Step 5). |
| **Product/Financial Delays (`Order Item Id`)** | Resolution must prioritize physical handling constraints and profit-margin protection. Expediting is restricted for low-margin SKUs (Reference Steps 3 & 4). |
| **Temporal/Operational Delays (`ship_hour`)** | Resolution must evaluate warehouse cutoff times and time-of-day infrastructure congestion. Expediting is only permitted if the dispatch window is still open (Reference Steps 2 & 6). |
| **Geographic-Related Delays** | Resolution must account for regional customs, regulatory constraints, or infrastructure limits. If bypass is impossible, escalation is mandatory (Reference Step 6). |

##### Step 7.3 Escalation and Governance
* Actions that exceed predefined cost limits or policy thresholds must be escalated with documented justification.
* If no suitable automated action exists, the case is escalated or resolved through customer notification.
* All decisions must record the identified cause of delay, resolution path, and justification for audit purposes.

---

### 6. Exclusions and Assumptions
* Raw timestamps are not used directly for operational decision-making.
* Personal identifiers and fine-grained location data are excluded.
* This SOP does not assume specific carrier contracts or warehouse operating schedules.

---

### 7. Revision Control
* **Version 1.1 — Approved SOP**
* This version establishes DataCo’s standard approach to late delivery assessment and response. Operational thresholds and configuration parameters may be updated without revising this SOP.

---

### 8. Intended Use
This SOP supports:
* Operational decision support systems,
* Automated planning and evaluation tools,
* Human supervisory oversight, and
* Consistent, explainable delivery resolution practices.
```