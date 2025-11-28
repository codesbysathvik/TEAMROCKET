from predict import predict_url

if __name__ == "__main__":
    print("\n🔍 ML Engine Ready\n")
    test = input("Enter URL text to evaluate: ")
    result = predict_url(test)
    print("\nResult:", result)