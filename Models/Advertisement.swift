import Foundation

// Модель для пагинированного ответа
struct PaginatedResponse<T: Codable>: Codable {
    let count: Int
    let next: String?
    let previous: String?
    let results: [T]
}

// Модель объявления
struct Advertisement: Codable, Identifiable {
    let id: Int
    let title: String
    let price: String
    let category: Category
    let author: User
    let status: String
    let location: String
    let isFeatured: Bool
    let viewsCount: Int
    let primaryImage: String?
    let imagesCount: Int
    let createdAt: String
    let updatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, title, price, category, author, status, location
        case isFeatured = "is_featured"
        case viewsCount = "views_count"
        case primaryImage = "primary_image"
        case imagesCount = "images_count"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

