#!/usr/bin/env python3

import sys
sys.path.insert(0, '/app')

from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin

def test_direct_handlers():
    try:
        plugin = SimpleAmoCRMPlugin()
        handlers = plugin.register_handlers()
        
        print(f"Handlers count: {len(handlers)}")
        print("\nAll handlers:")
        for name in sorted(handlers.keys()):
            handler = handlers[name]
            print(f"  {name}: {handler}")
            
        # Проверяем, что методы существуют
        print("\nChecking methods exist:")
        missing = []
        for name, handler in handlers.items():
            if handler is None:
                missing.append(name)
                print(f"  ❌ {name}: None")
            else:
                print(f"  ✅ {name}: OK")
                
        if missing:
            print(f"\n❌ Missing handlers: {missing}")
        else:
            print(f"\n✅ All handlers OK")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_handlers() 