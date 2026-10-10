#if os(macOS)
import Foundation

struct NativeModelURLTransport: NativeModelTransport {
    // Tests can inject URLProtocol through this factory without opening a network connection.
    let configuration: @Sendable () -> URLSessionConfiguration
    init(configuration: @escaping @Sendable () -> URLSessionConfiguration = { .ephemeral }) {
        self.configuration = configuration
    }
    static func allowed(_ url: URL) -> Bool {
        url.scheme == "https" && ["github.com", "release-assets.githubusercontent.com"].contains(url.host ?? "")
            && url.user == nil && url.password == nil && url.fragment == nil && url.port == nil
    }
    static func redirected(_ request: URLRequest, original: URLRequest?, count: Int) throws -> URLRequest {
        guard count <= 3, let url = request.url, allowed(url) else { throw NativeModelDownloader.Failure.redirectDenied }
        var clean = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 30)
        for field in ["Accept-Encoding", "Range", "If-Range"] {
            clean.setValue(original?.value(forHTTPHeaderField: field), forHTTPHeaderField: field)
        }
        return clean
    }
    func transfer(_ request: URLRequest,
                  response: @escaping @Sendable (HTTPURLResponse) throws -> Void,
                  chunk: @escaping @Sendable (Data) throws -> Void) async throws {
        guard let url = request.url, Self.allowed(url) else { throw NativeModelDownloader.Failure.redirectDenied }
        let config = configuration()
        config.urlCache = nil
        config.httpCookieStorage = nil
        config.httpShouldSetCookies = false
        config.urlCredentialStorage = nil
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 120
        let operation = NativeDownloadOperation(response: response, chunk: chunk)
        try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { continuation in
                operation.start(request, configuration: config, continuation: continuation)
            }
        } onCancel: { operation.cancel() }
    }
}

private final class NativeDownloadOperation: NSObject, URLSessionDataDelegate, @unchecked Sendable {
    let lock = NSLock()
    let receiveResponse: @Sendable (HTTPURLResponse) throws -> Void
    let receiveChunk: @Sendable (Data) throws -> Void
    var continuation: CheckedContinuation<Void, any Error>?
    var session: URLSession?
    var task: URLSessionDataTask?
    var failure: (any Error)?
    var cancelled = false
    var redirects = 0

    init(response: @escaping @Sendable (HTTPURLResponse) throws -> Void,
         chunk: @escaping @Sendable (Data) throws -> Void) {
        receiveResponse = response; receiveChunk = chunk
    }
    func start(_ request: URLRequest, configuration: URLSessionConfiguration,
               continuation: CheckedContinuation<Void, any Error>) {
        lock.lock()
        if cancelled { lock.unlock(); continuation.resume(throwing: CancellationError()); return }
        self.continuation = continuation
        let queue = OperationQueue()
        queue.maxConcurrentOperationCount = 1
        let session = URLSession(configuration: configuration, delegate: self, delegateQueue: queue)
        self.session = session
        let task = session.dataTask(with: request)
        self.task = task
        lock.unlock()
        task.resume()
    }
    func cancel() {
        lock.lock(); cancelled = true; let task = task; lock.unlock()
        task?.cancel()
    }
    func fail(_ error: any Error) {
        lock.lock(); if failure == nil { failure = error }; let task = task; lock.unlock()
        task?.cancel()
    }
    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive response: URLResponse,
                    completionHandler: @escaping @Sendable (URLSession.ResponseDisposition) -> Void) {
        do {
            guard let response = response as? HTTPURLResponse else { throw NativeModelDownloader.Failure.invalidResponse }
            try receiveResponse(response)
            completionHandler(.allow)
        } catch { fail(error); completionHandler(.cancel) }
    }
    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        do { try receiveChunk(data) } catch { fail(error) }
    }
    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: (any Error)?) {
        lock.lock()
        let continuation = continuation
        self.continuation = nil
        let result = cancelled ? CancellationError() : failure ?? error
        self.task = nil; self.session = nil
        lock.unlock()
        session.finishTasksAndInvalidate()
        if let result { continuation?.resume(throwing: result) } else { continuation?.resume() }
    }
    func urlSession(_ session: URLSession, task: URLSessionTask,
                    willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest,
                    completionHandler: @escaping @Sendable (URLRequest?) -> Void) {
        // The delegate queue is serial. Never forward cookies or authorization headers.
        redirects += 1
        do { completionHandler(try NativeModelURLTransport.redirected(request, original: task.originalRequest, count: redirects)) }
        catch { fail(error); completionHandler(nil) }
    }
    func urlSession(_ session: URLSession, task: URLSessionTask, didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping @Sendable (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        completionHandler(challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust
            ? .performDefaultHandling : .cancelAuthenticationChallenge, nil)
    }
}
#endif
