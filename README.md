# Lunar Survival Challenge: Collaborative Agent Architecture

![Architecture](https://github.com/PranavMishra17/NASA-Survival-on-the-moon--via-Agents/blob/47df41cb86326c0bf37d893a79cd1439c6bee4ad/arch.png)

## Paired Agent Teams

The system employs a collaborative approach with paired agent teams that work closely together before cross-team integration:

![Score](https://github.com/PranavMishra17/NASA-Survival-on-the-moon--via-Agents/blob/47df41cb86326c0bf37d893a79cd1439c6bee4ad/image_2025-03-18_185135062.png)

### Knowledge Acquisition Agents

#### 1. Science Analysis Agent
- **Role**: Information gathering on lunar environment
- **Focus**: Physics, environmental conditions, item properties in lunar context
- **Output**: Comprehensive knowledge base of scientific facts and principles
- **Key Considerations**: Vacuum mechanics, temperature gradients, radiation effects, gravity influence

#### 2. Resource Analysis Agent
- **Role**: Information gathering on human survival needs
- **Focus**: Human physiological requirements in extreme conditions
- **Output**: Structured hierarchy of survival needs with timeframes
- **Key Considerations**: Oxygen consumption rates, water needs, temperature regulation, psychological factors

### Technical Reasoning Team

#### 3. Science Reasoning Agent
- **Role**: Apply environmental knowledge to item evaluation
- **Collaborates With**: Protocol Reasoning Agent
- **Joint Output**: Technical ranking with science-based justifications
- **Collaborative Process**:
  - Science Agent proposes initial utility assessment
  - Protocol Agent challenges/validates based on procedures
  - Together they refine assessment through direct dialogue
  - Generate consensus technical perspective

#### 4. Protocol Reasoning Agent
- **Role**: Apply space agency procedures to item evaluation
- **Collaborates With**: Science Reasoning Agent
- **Joint Output**: Technical ranking with procedure-based justifications
- **Collaborative Process**:
  - Protocol Agent identifies standard protocols
  - Science Agent validates feasibility in lunar conditions
  - Together they identify procedure adaptations needed
  - Generate protocol-compliant recommendations

### Practical Reasoning Team

#### 5. Resource Reasoning Agent
- **Role**: Optimize survival resource allocation
- **Collaborates With**: Creative Reasoning Agent
- **Joint Output**: Practical ranking with resource optimization justifications
- **Collaborative Process**: 
  - Resource Agent proposes survival-critical priorities
  - Creative Agent challenges with alternative scenarios
  - Together they identify resource dependencies and synergies
  - Generate resource-optimized recommendations

#### 6. Creative Reasoning Agent
- **Role**: Consider edge cases and alternative item uses
- **Collaborates With**: Resource Reasoning Agent
- **Joint Output**: Practical ranking with contingency planning
- **Collaborative Process**:
  - Creative Agent proposes alternative item uses
  - Resource Agent validates practicality and impact
  - Together they identify multi-purpose items and creative solutions
  - Generate adaptable survival strategies

### Meta Reasoning Agent

#### 7. Meta Reasoning Agent
- **Role**: Integrate team perspectives and resolve conflicts
- **Input**: Technical and Practical team rankings with justifications
- **Process**: Holistic consideration of all perspectives
- **Output**: Final consensus ranking with comprehensive justifications

![Rank table](https://github.com/PranavMishra17/NASA-Survival-on-the-moon--via-Agents/blob/47df41cb86326c0bf37d893a79cd1439c6bee4ad/image_2025-03-18_185112195.png)
![Rank viz](https://github.com/PranavMishra17/NASA-Survival-on-the-moon--via-Agents/blob/47df41cb86326c0bf37d893a79cd1439c6bee4ad/image_2025-03-18_185149938.png)

## Collaborative Reasoning Framework

### 1. Knowledge Exchange Process (Within Teams)
```
Team Reasoning Loop:
   1. Agent A presents initial assessment of item
   2. Agent B asks critical questions based on expertise
   3. Agent A refines assessment based on B's perspective
   4. Agent B proposes complementary insights
   5. Together formulate integrated justification
   6. Repeat for each item until team consensus reached
```

### 2. Cross-Team Deliberation Process
```
Cross-Team Integration:
   1. Technical Team presents ranking with justifications
   2. Practical Team identifies areas of agreement/disagreement
   3. For each significant disagreement:
      a. Both teams present core reasoning
      b. Teams identify shared values and priorities
      c. Teams propose integrated ranking and justification
   4. Generate combined perspective incorporating both technical and practical aspects
```

### 3. Conflict Resolution Protocol
```
For items with significant ranking discrepancy:
   1. Identify specific reason for disagreement
   2. Evaluate time-criticality impact
   3. Consider scenario-specific contexts
   4. Assess confidence levels from both teams
   5. Document reasoning from both perspectives
   6. Meta Agent facilitates final decision with explicit rationale
```

### 4. Meta-Reasoning Process
```
Holistic Integration:
   1. Review team rankings and integrated justifications
   2. Identify remaining ambiguities or conflicts
   3. Apply scenario-specific contextual factors
   4. Consider interdependencies between items
   5. Evaluate overall survival strategy coherence
   6. Generate final ranking with multi-level justifications
```

## Reasoning Approach

The collaborative reasoning approach employs structured frameworks rather than simple numeric weighting:

### Item Analysis Framework
Each item is evaluated through multiple dimensions:

1. **Environmental Compatibility**: How the item functions in lunar conditions
2. **Survival Utility**: Direct contribution to keeping humans alive
3. **Time Sensitivity**: How quickly the item becomes critical
4. **Versatility**: Multiple use potential in different scenarios
5. **Dependency Role**: How item affects usefulness of other items

### Team Collaboration Mechanics

The paired agent design enables:

1. **Real-time knowledge refinement** - Agents continuously update their understanding through dialogue
2. **Complementary perspective integration** - Different expertise combined within each assessment
3. **Belief revision through questioning** - Agents challenge each other's assumptions
4. **Emergent insight development** - New understanding developed through collaborative dialogue

### Decision Framework

Final decisions rely on explicit reasoning rather than numeric calculations:

1. Identify the **critical survival functions** needed in lunar context
2. Map items to these functions with **specific mechanisms of utility**
3. Establish **logical dependencies** between items
4. Consider **time-phased needs** from immediate to long-term
5. Integrate **contingency planning** for key failure points
6. Document complete **chain of reasoning** for each decision
