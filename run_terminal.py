import initializers
import interaction


if __name__ == '__main__':
    initializers.run_all()

    terminal_prompt = interaction.main_prompt

    terminal_prompt.cmdloop()
