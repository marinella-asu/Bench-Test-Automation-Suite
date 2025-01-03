def reset(self):
        self.b1500.write("*rst; status:preset; *cls")