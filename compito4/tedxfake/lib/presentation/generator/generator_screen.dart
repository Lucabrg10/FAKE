// lib/presentation/generator/generator_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/post_generator_provider.dart';

class GeneratorScreen extends ConsumerWidget {
  final TextEditingController promptController = TextEditingController();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final postState = ref.watch(generatedPostProvider);
    final postNotifier = ref.read(generatedPostProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: Text("Genera Fake News")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: promptController,
              decoration: InputDecoration(labelText: "Scrivi un prompt"),
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                final prompt = promptController.text;
                if (prompt.isNotEmpty) {
                  postNotifier.generate(prompt); // ⬅️ chiamata al provider
                }
              },
              child: Text("Genera"),
            ),
            SizedBox(height: 32),
            // UI reattiva allo stato del provider
            postState.when(
              data: (post) => post == null
                  ? Text("Nessun post generato ancora")
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text("Titolo: ${post.title}", style: TextStyle(fontWeight: FontWeight.bold)),
                        Text("Testo: ${post.text}"),
                        Text("Autore: ${post.author}"),
                        Image.network(post.imageUrl),
                      ],
                    ),
              loading: () => CircularProgressIndicator(),
              error: (e, _) => Text("Errore: $e"),
            ),
          ],
        ),
      ),
    );
  }
}
