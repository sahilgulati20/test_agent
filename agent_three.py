import matplotlib.pyplot as plt

class AgentThree:
    def compare_and_visualize(self, user_doc: str, news_doc: str):
        print("\nUser Document:\n", user_doc)
        print("\nNews Document:\n", news_doc)

        categories = ['Advantages', 'Disadvantages']
        user_scores = [7, 3]      # Example static values
        news_scores = [6, 4]

        x = range(len(categories))
        plt.bar(x, user_scores, width=0.4, label='User Tech', align='center')
        plt.bar(x, news_scores, width=0.4, label='News Tech', align='edge')
        plt.xticks(x, categories)
        plt.legend()
        plt.title('Technology Comparison')
        plt.show()
