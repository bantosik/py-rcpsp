class ResourceUsage(dict):
    def add_resource_usage(self, demand):
        """
        Resources demand are added to self.
        
        :param demand: dictionary of resource demands to be added to self  
        """
        for resource, amount in demand.iteritems():
            if resource in self:
                self[resource] = self[resource] + amount
            else:
                self[resource] = amount
                
    def is_resource_usage_greater_than_supply(self, resource_supply):
        """
        Checks if usage of resource does not exceed overall supply (resource_supply)
        
        :param self: state of usage which is to be checked
        :param resource_supply: actual supply of resources
        """
        for resource in resource_supply:
            if resource not in self:
                continue    
            if self[resource] > resource_supply[resource]:
                return True
        else:
            return False
            
def update_resource_usages_in_time(resource_usages_in_time, activity, point_in_time):
    for point in range(point_in_time, point_in_time + activity.duration):
        actual_resource_usage = resource_usages_in_time[point]
        actual_resource_usage.add_resource_usage(activity.demand)
    
