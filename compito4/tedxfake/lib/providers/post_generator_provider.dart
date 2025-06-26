// lib/providers/post_generator_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/fake_news_api_service.dart';
import '../data/models/post.dart';

final apiServiceProvider = Provider((ref) => FakeNewsApiService());

final generatedPostProvider =
    AsyncNotifierProvider<PostGeneratorNotifier, Post?>(
  () => PostGeneratorNotifier(),
);

class PostGeneratorNotifier extends AsyncNotifier<Post?> {
  @override
  Future<Post?> build() async => null;

  Future<void> generate(String prompt) async {
    state = const AsyncLoading(); // Mostra loading nella UI

    final api = ref.read(apiServiceProvider);

    try {
      final post = await api.generateFakePost(prompt);
      state = AsyncData(post); // Stato aggiornato con dati
    } catch (e, st) {
      state = AsyncError(e, st); // Stato aggiornato con errore
    }
  }
}
