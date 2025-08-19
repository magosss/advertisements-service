import Foundation
import Combine

class AdvertisementsViewModel: ObservableObject {
    @Published var advertisements: [Advertisement] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService()
    private var cancellables = Set<AnyCancellable>()
    
    func loadAdvertisements() {
        isLoading = true
        errorMessage = nil
        
        print("🔄 Начинаем загрузку объявлений...")
        
        apiService.fetchAdvertisements()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                        print("❌ Ошибка загрузки объявлений: \(error)")
                    }
                },
                receiveValue: { [weak self] advertisements in
                    self?.advertisements = advertisements
                    print("✅ Загружено \(advertisements.count) объявлений")
                }
            )
            .store(in: &cancellables)
    }
}

