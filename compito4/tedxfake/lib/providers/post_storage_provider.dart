import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/post_storage_service.dart';
import '../data/models/post.dart';

final postStorageServiceProvider = Provider<PostStorageService>((ref) {
  return PostStorageService(baseUrl: 'https://8ev7cfo96k.execute-api.us-east-1.amazonaws.com/default/savePostMongoDB'); 
});

final postStorageNotifierProvider =
    AsyncNotifierProvider<PostStorageNotifier, void>(() => PostStorageNotifier());

class PostStorageNotifier extends AsyncNotifier<void> {
   @override
  Future<void> build() async {
    // Non serve inizializzazione, lascialo vuoto
  }
  Future<void> savePost(Post post) async {
    state = const AsyncLoading();
    final service = ref.read(postStorageServiceProvider);
    try {
      final success = await service.savePost(post);
      if (!success) throw Exception('Errore nel salvataggio');
      state = const AsyncData(null);
    } catch (e, st) {
      state = AsyncError(e, st);
      rethrow;
    }
  }
}
