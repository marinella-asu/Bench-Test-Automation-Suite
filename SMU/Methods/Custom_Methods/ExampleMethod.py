def Example(self, 
                b1500=None,  #Required
                param_name=None, #Required
                Example1 = None, ######CHANGE OR ADD VARIABLES HERE
                Example2 = None, ######CHANGE OR ADD VARIABLES HERE
                Example3 = None, ######CHANGE OR ADD VARIABLES HERE
                **overrides):

    # Collect defaults into a dict
    final_params = { #Required
        "Example1": Example1, ######CHANGE OR ADD VARIABLES HERE
        "Example2": Example2, ######CHANGE OR ADD VARIABLES HERE
        "Example3": Example3 ######CHANGE OR ADD VARIABLES HERE
    }

    #Required
    # If we were given b1500 + param_name, load values from parameters
    if b1500 and param_name:
        param_block = dict(b1500.parameters.get(param_name, {}))
        param_block.update(overrides)  # Apply runtime overrides

        # Attach as individual attributes to b1500 for global access
        for key, value in param_block.items():
            setattr(b1500, f"{key}_{param_name}", value)

        # Merge values from parameters with existing defaults
        final_params.update(param_block)

    # If we didn’t use parameters at all (case 3), just apply overrides directly
    if not b1500 or not param_name:
        final_params.update(overrides)
        

            
    # Unpack everything for use #Required
    Example1       = final_params["Example1"] ######CHANGE OR ADD VARIABLES HERE
    Example2       = final_params["Example2"] ######CHANGE OR ADD VARIABLES HERE
    Example3       = final_params["Example3"] ######CHANGE OR ADD VARIABLES HERE
     
    
    