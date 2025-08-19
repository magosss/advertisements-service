import Foundation
import Combine

class APIService: ObservableObject {
    private let baseURL = "https://turkobuv.ru/api"
    
    func fetchAdvertisements() -> AnyPublisher<[Advertisement], Error> {
        guard let url = URL(string: "\(baseURL)/advertisements/") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        print("🌐 Запрос к API: \(url)")
        
        return URLSession.shared.dataTaskPublisher(for: url)
            .tryMap { data, response in
                print("📡 Получен ответ от сервера")
                print("📊 Размер данных: \(data.count) байт")
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("📋 HTTP статус: \(httpResponse.statusCode)")
                    print("📋 HTTP заголовки: \(httpResponse.allHeaderFields)")
                }
                
                let responseString = String(data: data, encoding: .utf8) ?? "Не удалось декодировать"
                print("📄 Ответ сервера (первые 500 символов):")
                print(String(responseString.prefix(500)))
                
                return data
            }
            .decode(type: PaginatedResponse<Advertisement>.self, decoder: JSONDecoder())
            .map { $0.results }
            .eraseToAnyPublisher()
    }
    
    func fetchCategories() -> AnyPublisher<[Category], Error> {
        guard let url = URL(string: "\(baseURL)/categories/") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [Category].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
    
    func createAdvertisement(title: String, description: String, price: String, categoryId: Int, images: [Data]) -> AnyPublisher<Advertisement, Error> {
        guard let url = URL(string: "\(baseURL)/advertisements/") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "title": title,
            "description": description,
            "price": price,
            "category": categoryId
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            return Fail(error: error)
                .eraseToAnyPublisher()
        }
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: Advertisement.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
}

