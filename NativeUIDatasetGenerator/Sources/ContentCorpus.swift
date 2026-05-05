// ContentCorpus.swift
// NativeUIDatasetGenerator
//
// Deterministic, seeded text generator for realistic UI strings.
// Same seed → same output, every time.

import Foundation

// MARK: - Supporting Types

public enum DateFormat: String, Codable, Sendable {
    case mmmDYyyy  // "Jan 5, 2025"
    case dMmmYyyy  // "5 Jan 2025"
    case iso8601   // "2025-01-05"
}

public enum Currency: String, Codable, Sendable {
    case usd, eur, gbp, jpy, aed
}

// MARK: - ContentCorpus

public struct ContentCorpus: Sendable {
    private var rng: SeededRNG

    public init(seed: UInt64) {
        rng = SeededRNG(seed: seed)
    }

    // MARK: Person Names (500+)

    private static let personNames: [String] = [
        // Seed names (required)
        "Emma Chen", "James Okonkwo", "Priya Sharma", "Lucas Müller", "Fatima Al-Hassan",
        "Yuki Tanaka", "Maria Garcia", "Kwame Asante", "Aisha Patel", "Noah Kim",
        "Sofia Andersen", "Raj Krishnamurthy", "Amara Diallo", "Liam O'Sullivan", "Zara Kowalski",
        // European
        "Anna Schmidt", "Pierre Dupont", "Isabella Rossi", "Carlos Rodríguez", "Elena Petrov",
        "Hans Weber", "Claudia Bianchi", "Antoine Moreau", "Ingrid Larsson", "Sven Johansson",
        "Katarzyna Wiśniewska", "Tomáš Novák", "Birgit Hansen", "Nils Andersen", "Fiona MacLeod",
        "Patrick O'Brien", "Siobhan Murphy", "Conor Walsh", "Aoife Brennan", "Roisin Kelly",
        "Diego Fernández", "Carmen López", "Pablo Martínez", "Lucia Gómez", "Andrés Torres",
        "Giulia Ferrari", "Marco Esposito", "Valentina Bruno", "Francesco Conti", "Alessia Romano",
        "Mathieu Bernard", "Camille Petit", "Olivier Leroy", "Céline Martin", "Théo Girard",
        "Maximilian Bauer", "Franziska Hoffmann", "Klaus Fischer", "Monika Schulz", "Jürgen Meyer",
        "Piotr Kowalczyk", "Agnieszka Nowak", "Marek Wójcik", "Ewa Lewandowska", "Andrzej Zielinski",
        "Nikolai Volkov", "Tatiana Sokolova", "Dmitri Popov", "Irina Morozova", "Sergei Novikov",
        "Mihai Popescu", "Ioana Constantin", "Bogdan Ionescu", "Andreea Stan", "Vlad Gheorghe",
        "Kristján Sigurdsson", "Björn Eriksson", "Sigríður Magnúsdóttir", "Guðmundur Jónsson", "Helga Pálsdóttir",
        "Lena Müller", "Felix Braun", "Hannah Krause", "Jonas Schwarz", "Miriam Fuchs",
        "Rafael Alves", "Ana Ferreira", "Bruno Costa", "Catarina Sousa", "Diogo Carvalho",
        "Stavros Papadopoulos", "Maria Nikolaou", "Giorgos Alexiou", "Eleni Georgiou", "Nikos Christou",
        // East Asian
        "Wei Zhang", "Li Mei Wang", "Jiaming Liu", "Xiaoxue Chen", "Tianyu Li",
        "Haruto Sato", "Akiko Yamamoto", "Kenji Watanabe", "Midori Kobayashi", "Takeshi Ito",
        "Ji-Ho Park", "Soo-Jin Lee", "Hyun-Woo Kim", "Eun-Jung Choi", "Min-Jun Cho",
        "Fang Xu", "Qian Zhou", "Hao Wu", "Ling Yang", "Peng Huang",
        "Rin Nakamura", "Sota Kimura", "Hana Hayashi", "Ryo Shimizu", "Yuna Ogawa",
        "Bo-Ram Jung", "Da-Eun Han", "Jae-Won Oh", "Ji-Young Yoon", "Seung-Hyun Shin",
        "Bao Nguyen", "Lan Pham", "Tuan Tran", "Huong Le", "Minh Hoang",
        "Mei-Ling Ho", "Chun-Hui Lin", "Yen-Ting Tsai", "Shao-Hua Wu", "Chia-Yi Chang",
        "Aarav Gupta", "Pooja Mehta", "Rahul Joshi", "Ananya Singh", "Arjun Nair",
        "Ravi Iyer", "Deepa Pillai", "Suresh Menon", "Kavitha Reddy", "Vikram Malhotra",
        // South & Southeast Asian
        "Nurul Ain", "Ahmad Razif", "Siti Fatimah", "Muhammad Haziq", "Nur Izzah",
        "Thida Win", "Kyaw Zin", "Aye Myat", "Htet Aung", "Zin Mar",
        "Kasem Srisuk", "Nattaya Charoenwong", "Somchai Prasertsri", "Wipada Lertjit", "Apinya Wongsai",
        "Rohan De Silva", "Chamari Perera", "Nuwan Bandara", "Dilshani Fernando", "Ruwan Jayawardena",
        "Arjuna Wickramasinghe", "Sachini Kumari", "Dinesh Rajapaksa", "Malani Gunasekara", "Prasad Jayasinghe",
        // South Asian
        "Zara Ahmed", "Omar Farooq", "Sana Malik", "Bilal Hussain", "Hina Qureshi",
        "Anjali Verma", "Kiran Desai", "Manish Kapoor", "Shruti Pandey", "Amit Choudhary",
        "Tanvir Hossain", "Rima Begum", "Kamal Uddin", "Nasrin Akter", "Rafiqul Islam",
        // Middle Eastern & North African
        "Layla Al-Amin", "Omar Al-Rashid", "Nour El-Din", "Yasmine Khalil", "Kareem Hassan",
        "Rania Mansour", "Ahmed Farouk", "Dina Sabry", "Tariq Yousef", "Heba Mostafa",
        "Salam Al-Jabri", "Mariam Al-Farsi", "Yousef Al-Kindi", "Noura Al-Sayed", "Khalid Al-Mutairi",
        "Leila Benali", "Karim Boudali", "Samia Cherif", "Rachid Mabrouk", "Amina Tazi",
        "Hind El Fassi", "Youssef Benjelloun", "Zineb Chraibi", "Mehdi Ouali", "Nadia Berrada",
        // Sub-Saharan African
        "Chidi Eze", "Ngozi Okafor", "Emeka Nwosu", "Chioma Adeyemi", "Tunde Olawale",
        "Seun Akinlade", "Bisi Fashola", "Femi Okonkwo", "Yetunde Coker", "Biodun Adebayo",
        "Abena Mensah", "Kofi Boateng", "Akosua Amoah", "Yaw Darko", "Ama Sarpong",
        "Tendai Moyo", "Rutendo Chikwanda", "Takudzwa Mhlanga", "Nyasha Dube", "Tawanda Chikowore",
        "Sipho Dlamini", "Nomvula Zulu", "Thabo Molefe", "Lerato Sithole", "Bongani Khumalo",
        "Amara Kourouma", "Kadiatou Bah", "Mamadou Diallo", "Fatoumata Camara", "Ibrahim Sow",
        "Aminata Coulibaly", "Seydou Keita", "Mariam Traoré", "Oumar Sanogo", "Nana Koné",
        "Nkechi Aidoo", "Yemi Dada", "Folake Oyewole", "Gbemisola Adeyinka", "Rotimi Badmus",
        // Latin American
        "Valentina Pérez", "Sebastián Castro", "Camila Vargas", "Mateo Herrera", "Isabella Flores",
        "Santiago Ramírez", "Sofía Morales", "Nicolás Jiménez", "Martina Guerrero", "Emilio Navarro",
        "Lucía Ramos", "Alejandro Cruz", "Daniela Reyes", "Fernando Mendez", "Gabriela Ríos",
        "Rodrigo Vega", "Catalina Muñoz", "Andrés Rojas", "Paula Sánchez", "Miguel Ángel Cortés",
        "Beatriz Carvalho", "Henrique Santos", "Larissa Oliveira", "Gustavo Pereira", "Letícia Souza",
        "Thiago Rodrigues", "Mariana Ferreira", "Eduardo Almeida", "Juliana Costa", "Leonardo Gomes",
        "Ximena Aguilar", "Ernesto Vásquez", "Mónica Salinas", "Iván Fuentes", "Alejandra Espinoza",
        // North American
        "Tyler Johnson", "Madison Williams", "Brandon Davis", "Ashley Thompson", "Derek Anderson",
        "Brittany Wilson", "Kyle Martinez", "Amber Robinson", "Justin Clark", "Megan Rodriguez",
        "Caleb Lewis", "Samantha Lee", "Nathan Walker", "Kayla Hall", "Trevor Allen",
        "Lauren Young", "Garrett Hernandez", "Natalie King", "Dustin Wright", "Chelsea Lopez",
        "Zoe Mitchell", "Ethan Scott", "Chloe Green", "Mason Adams", "Lily Baker",
        "Elijah Nelson", "Avery Carter", "Grayson Perez", "Hazel Roberts", "Hudson Turner",
        "Scarlett Phillips", "Oliver Campbell", "Violet Parker", "Benjamin Evans", "Aurora Edwards",
        "Henry Collins", "Stella Stewart", "Jack Sanchez", "Nora Morris", "Owen Rogers",
        "Riley Reed", "Wyatt Cook", "Layla Morgan", "Levi Bell", "Eleanor Murphy",
        "Lincoln Bailey", "Hannah Rivera", "Isaac Cooper", "Addison Richardson", "Caleb Cox",
        "Brooklyn Howard", "Sebastian Ward", "Aubrey Torres", "Jackson Peterson", "Savannah Gray",
        "Aiden Ramirez", "Paisley James", "Carter Watson", "Skylar Brooks", "Jayden Kelly",
        "Peyton Sanders", "Dominic Price", "Reagan Bennett", "Jonah Wood", "Quinn Barnes",
        "Sawyer Ross", "Kennedy Henderson", "Easton Coleman", "Mackenzie Jenkins", "Declan Perry",
        // Additional diverse names
        "Hiroshi Yamada", "Sakura Fujii", "Keiko Hayashi", "Daisuke Matsumoto", "Naomi Abe",
        "Jin-Soo Kwon", "Hae-Won Oh", "Sang-Woo Park", "Mi-Rae Yoon", "Joon-Ki Lee",
        "Mei Chen", "Xiao-Han Li", "Zhen-Wei Liu", "Rui-Xuan Zhang", "Jia-Yi Wang",
        "Pranav Krishnan", "Divya Nambiar", "Siddharth Rao", "Meera Subramaniam", "Kartik Venkatesh",
        "Nadia Hassan", "Tariq Ibrahim", "Leilani Kahananui", "Keoni Makoa", "Ailani Kahale",
        "Miroslava Dvorak", "Radovan Blažek", "Veronika Horáček", "Ondřej Procházka", "Markéta Šimánek",
        "Luka Horvat", "Ana Kovač", "Marko Blažević", "Maja Jurić", "Ivan Perić",
        "Petros Stavros", "Dimitra Alexandros", "Konstantinos Dimos", "Theodora Vassilis", "Alexandros Nikos",
        "Eszter Varga", "Zsolt Kovács", "Katalin Szabó", "Péter Horváth", "Ágnes Tóth",
        "Marta Kowalska", "Michał Lewandowski", "Joanna Dąbrowska", "Paweł Wróbel", "Magdalena Szymańska",
        "Bogumił Kaczmarek", "Renata Piotrowska", "Tadeusz Grabowski", "Halina Nowakowska", "Zbigniew Mazur",
        "Amara Sow", "Ibrahima Diop", "Adja Thiam", "Moussa Fall", "Rokhaya Gueye",
        "Fatou Diagne", "Cheikh Mbaye", "Astou Ndiaye", "Pape Faye", "Mame Diarra Sarr",
        "Abubakar Sadiq", "Hauwa Musa", "Ismail Garba", "Ramatu Ibrahim", "Yakubu Aliyu",
        "Tendai Sithole", "Rumbidzai Ndlovu", "Farai Mutasa", "Gamuchirai Chigumbura", "Tafadzwa Magaya",
        "Oluwaseun Okafor", "Adaobi Nwosu", "Chukwuemeka Eze", "Ifeoma Igwe", "Obiageli Anyanwu",
        "Xolani Dlamini", "Nokukhanya Hadebe", "Mthokozisi Ndaba", "Lungelo Mhlongo", "Nokwanda Ntanzi",
        "Jeannette Uwimana", "Olivier Ndayishimiye", "Marie-Claire Habimana", "Jean-Pierre Nzeyimana", "Claudine Mukamana",
        "Celestino Mwangi", "Wanjiru Kamau", "Kiptoo Koech", "Achieng Odhiambo", "Mwende Mutua",
        "Gao Yan", "Sun Li", "Ding Fang", "Xu Wei", "Chen Jing",
        "Wang Fang", "Zhang Min", "Liu Yang", "Li Hua", "Zhao Lei",
        "Aryan Kapoor", "Neha Gupta", "Rohit Sharma", "Simran Kaur", "Harpreet Singh",
        "Gurpreet Dhaliwal", "Manpreet Sandhu", "Sukhwinder Gill", "Jaswinder Brar", "Ranjit Grewal",
        "Esperanza Vidal", "Tomás Delgado", "Concepción Ibáñez", "Aurelio Casas", "Remedios Blanco",
        "Pilar Suárez", "Adolfo Calvo", "Encarnación Montoya", "Enrique Rubio", "Soledad Romero",
        "Florentin Diaconu", "Sorina Popa", "Dorel Marin", "Luminița Dumitru", "Cosmin Badea",
        "Octavia Stoica", "Viorel Cristea", "Roxana Gheorghiu", "Adrian Mocanu", "Elvira Radu",
        "Radu Ionescu", "Anca Florescu", "Marian Neagu", "Daniela Zamfir", "Cristian Voicu",
        "Arnav Bose", "Rupali Chatterjee", "Subhash Banerjee", "Madhuri Das", "Tapas Ghosh",
        "Anindita Roy", "Partha Mukherjee", "Swati Sengupta", "Debashis Bhattacharya", "Mousumi Chakraborty",
        "Komal Thakur", "Gaurav Mathur", "Shweta Agarwal", "Mohit Srivastava", "Ruchi Mishra",
        "Akbar Hussain", "Rizwana Siddiqui", "Farhan Sheikh", "Naila Mirza", "Salman Baig",
    ]

    // MARK: Place Names (200+)

    private static let placeNames: [String] = [
        // World cities
        "Tokyo", "New York City", "London", "Paris", "Sydney",
        "Berlin", "Toronto", "Singapore", "Dubai", "Seoul",
        "Mumbai", "Mexico City", "São Paulo", "Lagos", "Istanbul",
        "Cairo", "Jakarta", "Nairobi", "Buenos Aires", "Moscow",
        "Los Angeles", "Chicago", "San Francisco", "Houston", "Miami",
        "Amsterdam", "Barcelona", "Rome", "Vienna", "Zürich",
        "Copenhagen", "Stockholm", "Helsinki", "Oslo", "Brussels",
        "Dublin", "Lisbon", "Athens", "Warsaw", "Prague",
        "Budapest", "Bucharest", "Kyiv", "Baku", "Tashkent",
        "Karachi", "Lahore", "Dhaka", "Colombo", "Kathmandu",
        "Bangkok", "Kuala Lumpur", "Manila", "Ho Chi Minh City", "Hanoi",
        "Taipei", "Hong Kong", "Shanghai", "Beijing", "Guangzhou",
        "Osaka", "Kyoto", "Sapporo", "Fukuoka", "Nagoya",
        "Riyadh", "Jeddah", "Abu Dhabi", "Doha", "Kuwait City",
        "Casablanca", "Tunis", "Algiers", "Accra", "Dakar",
        "Addis Ababa", "Kigali", "Kampala", "Dar es Salaam", "Lusaka",
        "Cape Town", "Johannesburg", "Durban", "Harare", "Maputo",
        "Kinshasa", "Abuja", "Kumasi", "Bamako", "Niamey",
        "Bogotá", "Lima", "Santiago", "Caracas", "Quito",
        "Auckland", "Melbourne", "Brisbane", "Perth", "Adelaide",
        // Neighborhoods & districts
        "Shibuya", "Ginza", "Shinjuku", "Harajuku", "Akihabara",
        "Midtown Manhattan", "Brooklyn Heights", "SoHo", "Greenwich Village", "Harlem",
        "Notting Hill", "Shoreditch", "Mayfair", "Canary Wharf", "Camden",
        "Le Marais", "Montmartre", "Saint-Germain-des-Prés", "Belleville", "Bastille",
        "Mitte", "Prenzlauer Berg", "Kreuzberg", "Neukölln", "Charlottenburg",
        "The Rocks", "Surry Hills", "Bondi", "Newtown", "Glebe",
        "Gangnam", "Itaewon", "Hongdae", "Myeong-dong", "Insadong",
        "Bandra West", "Colaba", "Powai", "Juhu", "Lower Parel",
        "Wan Chai", "Mong Kok", "Tsim Sha Tsui", "Central", "Sheung Wan",
        "Marina Bay", "Tiong Bahru", "Katong", "Dempsey Hill", "Orchard",
        // Famous streets & landmarks
        "Baker Street", "Downing Street", "Fleet Street", "King's Road", "Oxford Street",
        "Fifth Avenue", "Sunset Boulevard", "Rodeo Drive", "Wall Street", "Broadway",
        "Champs-Élysées", "Rue de Rivoli", "Avenue Montaigne", "Rue du Faubourg Saint-Honoré", "Boulevard Haussmann",
        "Via Condotti", "Via Veneto", "Corso Vittorio Emanuele", "Piazza Navona", "Campo de' Fiori",
        "Ramblas", "Passeig de Gràcia", "Gran Via", "Calle Serrano", "Puerta del Sol",
        "Central Park", "Golden Gate Park", "Hyde Park", "Tiergarten", "Bois de Boulogne",
        "Shibuya Crossing", "Times Square", "Piccadilly Circus", "Trafalgar Square", "Place de la Bastille",
        "Covent Garden", "Borough Market", "Portobello Road Market", "Camden Market", "Columbia Road",
        // Venue types & named places
        "Grand Central Terminal", "Victoria Station", "Gare du Nord", "Hauptbahnhof Berlin", "Tokyo Station",
        "Heathrow Airport", "Charles de Gaulle Airport", "JFK International", "Changi Airport", "Dubai International",
        "The Shard", "Burj Khalifa", "Empire State Building", "Eiffel Tower", "Big Ben",
        "Tate Modern", "Louvre", "MoMA", "Guggenheim", "Uffizi Gallery",
        "Ritz Carlton Suite", "Four Seasons Lobby", "Grand Hyatt Atrium", "Marriott Courtyard", "Hilton Garden",
        "Whole Foods Market", "Trader Joe's", "Borough Market Stall", "Tsukiji Outer Market", "Mercado Central",
        "Raffles Hotel", "Mandarin Oriental", "Peninsula Hotel", "Savoy Hotel", "Claridge's",
        // Street addresses (generic)
        "14 Maple Avenue", "27 Oak Street", "103 Pine Road", "8 Elm Drive", "55 Cedar Lane",
        "201 Harbor View", "76 Hillside Court", "310 Riverside Drive", "42 Lakefront Boulevard", "9 Mountain Pass",
        "1600 Pennsylvania Avenue", "221B Baker Street", "10 Downing Street", "30 Rockefeller Plaza", "1 Infinite Loop",
    ]

    // MARK: Company Names (100+)

    private static let companyNames: [String] = [
        "Apex Solutions", "Verdant Labs", "Kestrel Systems", "Ironclad Technologies", "Luminary Digital",
        "Cobalt Analytics", "Meridian Software", "Pinnacle Works", "Orbis Consulting", "Stratum Group",
        "Nexus Dynamics", "Halcyon Ventures", "Vantage Technologies", "Crestwood Digital", "Sterling Networks",
        "Horizon Labs", "Catalyst Group", "Zenith Systems", "Ember Works", "Cinder Technologies",
        "Axiom Partners", "Beacon Analytics", "Cipher Solutions", "Delphi Consulting", "Echo Digital",
        "Forge Labs", "Granite Systems", "Harbor Networks", "Indigo Technologies", "Jade Ventures",
        "Kinetic Works", "Lattice Group", "Mosaic Solutions", "Nimbus Analytics", "Onyx Consulting",
        "Prism Digital", "Quantum Partners", "Raven Technologies", "Sapphire Labs", "Titan Systems",
        "Umbra Networks", "Vantage Works", "Wren Consulting", "Xenon Digital", "Yoke Technologies",
        "Zephyr Analytics", "Alder Group", "Birch Solutions", "Cedar Systems", "Dune Technologies",
        "Estuary Partners", "Fjord Labs", "Glade Analytics", "Heath Consulting", "Isle Technologies",
        "Jetstream Digital", "Knoll Systems", "Lark Networks", "Mast Solutions", "Nave Group",
        "Opal Technologies", "Peak Labs", "Quest Analytics", "Ridge Consulting", "Shore Digital",
        "Thorn Systems", "Uplift Technologies", "Vale Networks", "Ward Solutions", "Xact Group",
        "Yield Technologies", "Zeal Labs", "Ambit Analytics", "Brim Consulting", "Cove Digital",
        "Drift Systems", "Edge Technologies", "Flux Networks", "Glyph Solutions", "Halo Group",
        "Iris Labs", "Joule Consulting", "Keen Digital", "Link Technologies", "Mesh Analytics",
        "Node Solutions", "Orb Systems", "Plex Networks", "Quill Group", "Realm Technologies",
        "Silo Labs", "Trek Consulting", "Unit Digital", "Volt Systems", "Wave Analytics",
        "Arc Solutions", "Bay Technologies", "Core Networks", "Dot Consulting", "Era Digital",
        "Fox Systems", "Grit Analytics", "Hub Solutions", "Ink Technologies", "Jet Networks",
        "Kit Consulting", "Log Digital", "Map Systems", "Net Analytics", "Oak Solutions",
        "Pod Technologies", "Ray Networks", "Set Consulting", "Tap Digital", "Use Systems",
        "Via Analytics", "Web Solutions", "Xis Technologies", "Yaw Networks", "Zip Consulting",
    ]

    // MARK: Button Labels (50+)

    private static let buttonLabels: [String] = [
        "Continue", "Save Changes", "Get Started", "Sign In", "Sign Out",
        "Sign Up", "Create Account", "Log In", "Log Out", "Submit",
        "Cancel", "Done", "Next", "Back", "Finish",
        "Apply", "Confirm", "Delete", "Remove", "Add",
        "Edit", "Update", "Save", "Discard", "Close",
        "Share", "Download", "Upload", "Export", "Import",
        "Refresh", "Reload", "Retry", "Try Again", "Skip",
        "Later", "Remind Me Later", "Not Now", "Got It", "Learn More",
        "View Details", "See All", "Show More", "Show Less", "Expand",
        "Collapse", "Filter", "Sort", "Search", "Clear",
        "Reset", "Enable", "Disable", "Turn On", "Turn Off",
        "Allow", "Deny", "Accept", "Decline", "Agree",
        "Disagree", "Yes", "No", "Maybe", "OK",
        "Pay Now", "Add to Cart", "Buy Now", "Checkout", "Place Order",
        "Track Order", "View Order", "Reorder", "Return Item", "Request Refund",
        "Send Message", "Reply", "Forward", "Archive", "Mark Read",
        "Join Now", "Subscribe", "Unsubscribe", "Follow", "Unfollow",
        "Connect", "Disconnect", "Invite", "Report", "Block",
        "Change Password", "Forgot Password", "Reset Password", "Verify Email", "Send Code",
    ]

    // MARK: Navigation Titles (50+)

    private static let navigationTitles: [String] = [
        "Settings", "My Account", "Order History", "Profile", "Home",
        "Notifications", "Messages", "Search", "Explore", "Discover",
        "Favorites", "Saved Items", "Wishlist", "Cart", "Checkout",
        "Payment Methods", "Shipping Address", "Billing Info", "Order Details", "Track Package",
        "Help Center", "Support", "Contact Us", "About", "Privacy Policy",
        "Terms of Service", "Accessibility", "Appearance", "Notifications Settings", "Security",
        "Two-Factor Auth", "Connected Apps", "Data & Storage", "Language", "Region",
        "My Orders", "Returns", "Subscriptions", "Membership", "Rewards",
        "Dashboard", "Analytics", "Reports", "Insights", "Activity",
        "Photos", "Albums", "Documents", "Downloads", "Recent Files",
        "Contacts", "Groups", "Calendars", "Reminders", "Notes",
        "Health", "Fitness", "Sleep", "Nutrition", "Mindfulness",
        "Map", "Directions", "Nearby", "Saved Places", "History",
        "Library", "Playlists", "Podcasts", "Downloads", "Following",
        "Trending", "New Arrivals", "Best Sellers", "On Sale", "Featured",
        "Wallet", "Transactions", "Investments", "Budget", "Goals",
        "Projects", "Tasks", "Team", "Workspace", "Integrations",
    ]

    // MARK: List Row Titles (50+)

    private static let listRowTitles: [String] = [
        "Emma Chen", "Apex Solutions", "Central Park", "Order #48291", "iPhone 15 Pro",
        "James Okonkwo", "Verdant Labs", "Shibuya Crossing", "Invoice #7734", "MacBook Air",
        "Priya Sharma", "Kestrel Systems", "Baker Street", "Receipt #10023", "AirPods Pro",
        "Tokyo", "Project Alpha", "Meeting Notes", "Design Review", "Q3 Report",
        "London", "Project Beta", "Sprint Planning", "Code Review", "Annual Summary",
        "Sydney", "Ironclad Tech", "Times Square", "Ticket #5591", "iPad mini",
        "Lucas Müller", "Luminary Digital", "Montmartre", "Case #8847", "Apple Watch",
        "Fatima Al-Hassan", "Cobalt Analytics", "Notting Hill", "Booking #3320", "HomePod mini",
        "Morning Standup", "Team Sync", "Product Review", "User Research", "Strategy Session",
        "Yuki Tanaka", "Meridian Software", "Ginza", "Reservation #6612", "Smart TV 55\"",
        "Maria Garcia", "Pinnacle Works", "Harajuku", "Warranty #2241", "Wireless Charger",
        "Kwame Asante", "Orbis Consulting", "Brooklyn Heights", "Estimate #9905", "USB-C Hub",
        "Aisha Patel", "Stratum Group", "Gangnam", "Contract #4467", "Keyboard Pro",
        "Noah Kim", "Nexus Dynamics", "Le Marais", "Proposal #1138", "Mechanical Keyboard",
        "Sofia Andersen", "Halcyon Ventures", "Mitte", "Agreement #7790", "Monitor Stand",
        "Raj Krishnamurthy", "Vantage Tech", "Bandra West", "Draft #2256", "Desk Lamp",
        "Amara Diallo", "Crestwood Digital", "Covent Garden", "Form #8814", "Cable Organizer",
        "Liam O'Sullivan", "Sterling Networks", "Wan Chai", "Doc #3375", "Travel Adapter",
    ]

    // MARK: List Row Subtitles (50+)

    private static let listRowSubtitles: [String] = [
        "2 hours ago", "Yesterday at 3:42 PM", "Last week", "3 days ago", "Just now",
        "5 minutes ago", "1 hour ago", "This morning", "Monday", "Last month",
        "In transit", "Delivered", "Processing", "Shipped", "Cancelled",
        "Pending approval", "Under review", "Completed", "Draft", "Archived",
        "Due tomorrow", "Overdue", "Scheduled for Friday", "Starts in 2 hours", "Ends today",
        "$24.99", "$149.00", "$9.99/month", "$299.00", "Free",
        "High priority", "Medium priority", "Low priority", "Urgent", "On hold",
        "3 items", "12 messages", "5 unread", "2 attachments", "4 participants",
        "San Francisco, CA", "New York, NY", "London, UK", "Tokyo, Japan", "Sydney, Australia",
        "iOS 18", "macOS 15", "Version 3.2.1", "Build 1042", "Latest",
        "Active subscription", "Trial expires soon", "Renewal due", "Cancelled", "Paused",
        "512 GB used", "2.4 GB remaining", "Synced", "Backup complete", "Uploading...",
        "johndoe@example.com", "+1 (555) 867-5309", "Not verified", "Verified", "2FA enabled",
        "Shared with 3 people", "Private", "Team access", "Public", "Restricted",
        "Updated 5 min ago", "No recent activity", "Last seen today", "Online", "Away",
        "12 km away", "0.3 miles", "5-10 min walk", "Next bus in 4 min", "Open now",
        "4.8 ★ (1,204 reviews)", "4.2 ★ (89 reviews)", "New", "Trending", "Editor's Choice",
    ]

    // MARK: Email Parts

    private static let emailLocalPrefixes: [String] = [
        "emma.chen", "james.okonkwo", "priya.sharma", "lucas.muller", "fatima.hassan",
        "yuki.tanaka", "maria.garcia", "kwame.asante", "aisha.patel", "noah.kim",
        "sofia.andersen", "raj.k", "amara.diallo", "liam.o", "zara.kowalski",
        "user", "hello", "contact", "info", "support",
        "hi", "hey", "dev", "admin", "team",
        "mail", "inbox", "me", "work", "personal",
        "alex", "sam", "jordan", "taylor", "morgan",
        "casey", "riley", "quinn", "avery", "blake",
        "drew", "lee", "pat", "kim", "chris",
        "j.smith", "m.jones", "r.williams", "a.brown", "c.davis",
        "t.miller", "s.wilson", "d.moore", "e.taylor", "f.anderson",
    ]

    private static let emailDomains: [String] = [
        "example.com", "mail.com", "inbox.net", "webmail.org", "fastmail.io",
        "proton.me", "outlook.net", "icloud.com", "gmail.com", "yahoo.com",
        "company.com", "work.io", "corp.net", "office.org", "biz.com",
        "dev.io", "tech.com", "labs.net", "studio.co", "agency.io",
        "myemail.com", "privatebox.net", "securemail.org", "postbox.io", "letterbox.com",
        "uk.com", "eu.org", "ca.net", "au.com", "sg.io",
        "support.org", "help.com", "noreply.net", "team.io", "group.com",
    ]

    // MARK: URL Parts

    private static let urlSchemes: [String] = ["https://", "https://", "https://"]
    private static let urlSubdomains: [String] = [
        "www", "app", "api", "dev", "staging",
        "m", "mobile", "portal", "dashboard", "admin",
        "shop", "store", "checkout", "account", "auth",
        "blog", "news", "docs", "help", "support",
        "cdn", "static", "media", "files", "assets",
    ]
    private static let urlDomains: [String] = [
        "example.com", "myapp.io", "getservice.co", "useproduct.com", "tryplatform.net",
        "apexsolutions.com", "verdantlabs.io", "kestrel.systems", "luminary.digital", "cobalt.analytics",
        "meridian.software", "pinnacle.works", "orbis.consulting", "nexusdynamics.com", "halcyon.ventures",
        "devtools.io", "techplatform.com", "saasproduct.net", "cloudservice.io", "webplatform.co",
        "shopfront.com", "marketplace.io", "storefront.co", "retailhub.net", "shopnow.com",
    ]
    private static let urlPaths: [String] = [
        "/home", "/dashboard", "/settings", "/profile", "/account",
        "/products", "/categories", "/search", "/checkout", "/orders",
        "/blog", "/news", "/about", "/contact", "/help",
        "/pricing", "/features", "/docs", "/api", "/status",
        "/sign-in", "/sign-up", "/forgot-password", "/verify", "/onboarding",
        "/gallery", "/portfolio", "/case-studies", "/testimonials", "/partners",
        "", "", "/home", "/dashboard",
    ]

    // MARK: Date Parts

    private static let months: [(name: String, num: String)] = [
        ("Jan", "01"), ("Feb", "02"), ("Mar", "03"), ("Apr", "04"),
        ("May", "05"), ("Jun", "06"), ("Jul", "07"), ("Aug", "08"),
        ("Sep", "09"), ("Oct", "10"), ("Nov", "11"), ("Dec", "12"),
    ]

    // MARK: - Public API

    public mutating func personName() -> String {
        ContentCorpus.personNames.randomElement(using: &rng) ?? "Alex Johnson"
    }

    public mutating func placeName() -> String {
        ContentCorpus.placeNames.randomElement(using: &rng) ?? "New York"
    }

    public mutating func companyName() -> String {
        ContentCorpus.companyNames.randomElement(using: &rng) ?? "Apex Solutions"
    }

    public mutating func date(format: DateFormat) -> String {
        let year = Int(rng.next() % 5) + 2023  // 2023–2027
        let monthIdx = Int(rng.next() % 12)     // 0–11
        let day = Int(rng.next() % 28) + 1      // 1–28

        let month = ContentCorpus.months[monthIdx]

        switch format {
        case .mmmDYyyy:
            return "\(month.name) \(day), \(year)"
        case .dMmmYyyy:
            return "\(day) \(month.name) \(year)"
        case .iso8601:
            let dayStr = day < 10 ? "0\(day)" : "\(day)"
            return "\(year)-\(month.num)-\(dayStr)"
        }
    }

    public mutating func price(currency: Currency) -> String {
        // Generate value in cents: 99 to 999999 ($0.99 to $9,999.99)
        let cents = Int(rng.next() % 999_901) + 99
        let major = cents / 100
        let minor = cents % 100
        let minorStr = minor < 10 ? "0\(minor)" : "\(minor)"

        switch currency {
        case .usd:
            return "$\(major).\(minorStr)"
        case .eur:
            return "€\(major).\(minorStr)"
        case .gbp:
            return "£\(major).\(minorStr)"
        case .jpy:
            // JPY has no decimal; scale to yen range 1–9999
            let yen = Int(rng.next() % 9_999) + 1
            return "¥\(yen)円"
        case .aed:
            return "AED \(major).\(minorStr)"
        }
    }

    public mutating func email() -> String {
        let local = ContentCorpus.emailLocalPrefixes.randomElement(using: &rng) ?? "user"
        let domain = ContentCorpus.emailDomains.randomElement(using: &rng) ?? "example.com"
        return "\(local)@\(domain)"
    }

    public mutating func url() -> String {
        let subdomain = ContentCorpus.urlSubdomains.randomElement(using: &rng) ?? "www"
        let domain = ContentCorpus.urlDomains.randomElement(using: &rng) ?? "example.com"
        let path = ContentCorpus.urlPaths.randomElement(using: &rng) ?? ""
        return "https://\(subdomain).\(domain)\(path)"
    }

    public mutating func buttonLabel() -> String {
        ContentCorpus.buttonLabels.randomElement(using: &rng) ?? "Continue"
    }

    public mutating func navigationTitle() -> String {
        ContentCorpus.navigationTitles.randomElement(using: &rng) ?? "Settings"
    }

    public mutating func listRowTitle() -> String {
        ContentCorpus.listRowTitles.randomElement(using: &rng) ?? "Item"
    }

    public mutating func listRowSubtitle() -> String {
        ContentCorpus.listRowSubtitles.randomElement(using: &rng) ?? "Details"
    }
}
