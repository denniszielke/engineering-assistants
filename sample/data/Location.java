import java.util.Date;  
import java.util.List;  
  
public class Tool {  
    private int toolId;  
    private String category;  
    private String title;  
    private String description;  
    private List<Location> locations;  // References to locations  
    private Ownership ownership;       // Reference to ownership  
    private List<MaintenanceSchedule> maintenanceSchedules;  // References to maintenance schedules  
  
    // Constructors, getters, and setters  
}  
  
public class Location {  
    private int locationId;  
    private String locationName;  
    private String address;  
  
    // Constructors, getters, and setters  
}  
  
public class ToolLocation {  
    private int toolLocationId;  
    private Tool tool;       // Reference to Tool  
    private Location location;  // Reference to Location  
  
    // Constructors, getters, and setters  
}  
  
public class Ownership {  
    private int ownerId;  
    private String ownerName;  
    private String department;  
  
    // Constructors, getters, and setters  
}  
  
public class ToolOwnership {  
    private int toolOwnershipId;  
    private Tool tool;       // Reference to Tool  
    private Ownership ownership;  // Reference to Ownership  
  
    // Constructors, getters, and setters  
}  
  
public class Technician {  
    private int technicianId;  
    private String technicianName;  
  
    // Constructors, getters, and setters  
}  
  
public class MaintenanceSchedule {  
    private int scheduleId;  
    private Tool tool;       // Reference to Tool  
    private String frequency;  
    private Date nextDueDate;  
    private Technician technician;  // Reference to Technician  
  
    // Constructors, getters, and setters  
}  
