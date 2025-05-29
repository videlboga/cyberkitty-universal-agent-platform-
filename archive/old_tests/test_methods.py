#!/usr/bin/env python3

import sys
sys.path.insert(0, '/app')

from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin

def test_methods():
    plugin = SimpleAmoCRMPlugin()
    
    methods_to_check = [
        '_handle_get_contact',
        '_handle_list_contacts', 
        '_handle_delete_contact',
        '_handle_update_lead',
        '_handle_delete_lead',
        '_handle_get_lead',
        '_handle_list_leads',
        '_handle_get_account'
    ]
    
    print("Checking methods:")
    for method in methods_to_check:
        exists = hasattr(plugin, method)
        print(f"  {method}: {'✅' if exists else '❌'}")
        
        if exists:
            method_obj = getattr(plugin, method)
            print(f"    Type: {type(method_obj)}")

if __name__ == "__main__":
    test_methods() 