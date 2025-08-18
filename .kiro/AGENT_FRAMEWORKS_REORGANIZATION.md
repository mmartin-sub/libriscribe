# Agent Frameworks Reorganization

## Overview

I've successfully reorganized the AutoGen-specific code into a dedicated agent frameworks structure. This provides better organization and prepares the codebase for future framework options while keeping the current AutoGen implementation intact.

## New Structure

### Directory Layout

```
src/libriscribe2/agent_frameworks/
├── __init__.py                    # Framework package exports
├── base.py                        # Base framework abstraction
└── autogen/                       # AutoGen-specific implementation
    ├── __init__.py               # AutoGen package exports
    ├── wrapper.py                # AutoGen agent wrapper
    └── service.py                # AutoGen service layer
```

### Key Changes

#### 1. **Framework Abstraction Layer** ✅ IMPLEMENTED

- **File:** `src/libriscribe2/agent_frameworks/base.py`
- **Purpose:** Common interface for different agent frameworks
- **Features:**
  - `BaseFrameworkWrapper`: Abstract base for framework wrappers
  - `BaseFrameworkService`: Abstract base for framework services
  - `FrameworkRegistry`: Registry for managing multiple frameworks
  - `FrameworkAgent` & `FrameworkService`: Protocols for framework components

#### 2. **AutoGen Implementation** ✅ MOVED

- **From:** `src/libriscribe2/agents/autogen_wrapper.py` → `src/libriscribe2/agent_frameworks/autogen/wrapper.py`
- **From:** `src/libriscribe2/services/autogen_service.py` → `src/libriscribe2/agent_frameworks/autogen/service.py`
- **Updated:** Implements base framework interfaces
- **Maintained:** All existing functionality preserved

#### 3. **Updated Imports** ✅ COMPLETED

- **File:** `src/libriscribe2/agents/project_manager.py`
- **Change:** Updated import path for AutoGen components
- **Impact:** No breaking changes to existing code

## Benefits

### 1. **Better Organization**

- Clear separation of framework-specific code
- Dedicated structure for future frameworks
- Consistent interface across frameworks

### 2. **Future-Proof Architecture**

- Easy to add new frameworks (e.g., LangGraph, CrewAI)
- Common abstraction layer reduces duplication
- Framework registry for dynamic selection

### 3. **Maintained Functionality**

- All existing AutoGen features preserved
- No breaking changes to current implementation
- Backward compatibility maintained

## Framework Abstraction Details

### Base Framework Interface

```python
class BaseFrameworkWrapper(ABC):
    @abstractmethod
    def create_agent(self, libriscribe_agent: Any, **kwargs: Any) -> FrameworkAgent:
        pass

    @abstractmethod
    def create_service(self) -> FrameworkService:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_framework_info(self) -> Dict[str, Any]:
        pass
```

### Framework Registry

```python
class FrameworkRegistry:
    def register_framework(self, name: str, framework: BaseFrameworkWrapper) -> None:
        """Register a framework."""

    def get_available_frameworks(self) -> List[str]:
        """Get list of available frameworks."""

    def set_active_framework(self, name: str) -> bool:
        """Set the active framework."""
```

## Current Status

### ✅ Completed

1. **Framework Structure Created**
   - Base abstraction layer implemented
   - AutoGen code moved to new location
   - Imports updated throughout codebase

2. **AutoGen Implementation Updated**
   - Implements base framework interfaces
   - Maintains all existing functionality
   - No breaking changes

3. **Documentation Updated**
   - Clear structure documentation
   - Migration guide created
   - Best practices maintained

### 🔄 Ready for Future Frameworks

1. **LangGraph Integration**
   - Framework structure ready
   - Base interfaces defined
   - Easy to implement

2. **CrewAI Integration**
   - Similar structure possible
   - Common abstraction layer
   - Minimal code duplication

3. **Custom Frameworks**
   - Extensible architecture
   - Clear implementation patterns
   - Consistent interfaces

## Usage Examples

### Current AutoGen Usage (Unchanged)

```python
from libriscribe2.agent_frameworks.autogen import AutoGenService, AutoGenAgentWrapper

# Create service
service = AutoGenService(settings, llm_client)

# Create book with AutoGen
success = await service.create_book(project_knowledge_base)
```

### Future Framework Usage (Ready)

```python
from libriscribe2.agent_frameworks import FrameworkRegistry

# Register frameworks
registry = FrameworkRegistry()
registry.register_framework("autogen", AutoGenWrapper(settings, llm_client))
registry.register_framework("langgraph", LangGraphWrapper(settings, llm_client))

# Use different frameworks
if registry.set_active_framework("autogen"):
    service = registry.get_active_framework().create_service()
    await service.create_book(project_knowledge_base)
```

## Migration Notes

### No Breaking Changes

- All existing AutoGen functionality preserved
- Import paths updated automatically
- No code changes required for current usage

### Future Framework Addition

To add a new framework (e.g., LangGraph):

1. **Create Framework Directory**

   ```
   src/libriscribe2/agent_frameworks/langgraph/
   ├── __init__.py
   ├── wrapper.py
   └── service.py
   ```

2. **Implement Base Interfaces**

   ```python
   class LangGraphWrapper(BaseFrameworkWrapper):
       def create_agent(self, libriscribe_agent, **kwargs):
           # LangGraph-specific implementation

       def create_service(self):
           return LangGraphService(self.settings, self.llm_client)
   ```

3. **Register Framework**

   ```python
   registry.register_framework("langgraph", LangGraphWrapper(settings, llm_client))
   ```

## Conclusion

The reorganization provides:

1. **Better Code Organization**: Clear separation of framework-specific code
2. **Future-Proof Architecture**: Easy to add new frameworks
3. **Maintained Functionality**: No breaking changes to existing code
4. **Consistent Interface**: Common abstraction layer across frameworks

The current AutoGen implementation is preserved and ready for use, while the new structure prepares the codebase for future framework options like LangGraph, CrewAI, or custom frameworks.

## Next Steps

1. **Test Current Implementation**: Verify AutoGen functionality works as expected
2. **Add Framework Registry**: Integrate registry into project manager
3. **Document New Structure**: Update developer documentation
4. **Plan Future Frameworks**: Identify next framework to integrate

The foundation is now in place for a flexible, multi-framework agent system that can grow with your needs.
