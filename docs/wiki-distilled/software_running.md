# Where to Run Code at Fred Hutch

Source: https://sciwiki.fredhutch.org/scicomputing/software_running/

## Three Execution Environments

### 1. Local Computer
- **Advantages**: Immediate access, familiar environment
- **Disadvantages**: Limited CPU, memory and disk resources for large tasks

### 2. Shared Cluster Node (Rhino)
- **Advantages**: Higher CPU, memory and disk resources
- **Disadvantages**: File transfer requirements, internet dependency, potential slowdowns with concurrent users

### 3. Reserved Cluster Node (Gizmo)
- **Advantages**: Higher CPU, memory and disk resources, exclusive user access
- **Disadvantages**: File transfer needs, internet requirement, potential wait times for powerful machines

## Key Technical Guidance

Load programs via environmental modules rather than calling them directly:

```bash
ml R    # Use this, not just typing 'R' on rhino
```

This ensures:
- Reproducibility of code
- Access to the latest software versions available
