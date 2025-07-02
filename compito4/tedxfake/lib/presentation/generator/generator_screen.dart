import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/post_generator_provider.dart';
import '../../shared/widgets/post_card.dart';
import '../../providers/post_storage_provider.dart';

class GeneratorScreen extends ConsumerWidget {
  final TextEditingController promptController = TextEditingController();

  GeneratorScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final postState = ref.watch(generatedPostProvider);
    final postNotifier = ref.read(generatedPostProvider.notifier);
    final storageNotifier = ref.read(postStorageNotifierProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: Text("Genera Fake News")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
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
                    postNotifier.generate(prompt);
                  }
                },
                child: Text("Genera"),
              ),
              SizedBox(height: 32),
              postState.when(
                data:
                    (post) =>
                        post == null
                            ? Text("Nessun post generato ancora")
                            : Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                PostCard(post: post, compact: false,),
                                SizedBox(height: 20),
                                Row(
                                  children: [
                                    Expanded(
                                      child: ElevatedButton(
                                        onPressed: () {
                                          postNotifier.reset();
                                          promptController.clear();
                                        },
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: Colors.red,
                                        ),
                                        child: Text('Cancella'),
                                      ),
                                    ),
                                    SizedBox(width: 16),
                                    Expanded(
                                      child: ElevatedButton(
                                        onPressed: () async {
                                          try {
                                            await storageNotifier.savePost(
                                              post,
                                            );
                                            ScaffoldMessenger.of(
                                              context,
                                            ).showSnackBar(
                                              SnackBar(
                                                content: Text(
                                                  'Post salvato con successo!',
                                                ),
                                              ),
                                            );
                                            postNotifier.reset();
                                            promptController.clear();
                                          } catch (e) {
                                            ScaffoldMessenger.of(
                                              context,
                                            ).showSnackBar(
                                              SnackBar(
                                                content: Text(
                                                  'Errore nel salvataggio: $e',
                                                ),
                                              ),
                                            );
                                          }
                                        },

                                        child: Text('Salva'),
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                loading: () => Center(child: CircularProgressIndicator()),
                error: (e, _) => Text("Errore: $e"),
              ),
            ],
          ),
        ),
      ),
    );
  }

}
