# Werewolves Game Backend

This is the backend for werewolve game with PvP and PvE modes

## Usage

### Deployment

In order to deploy, you need to run the following command:

```
$ serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying werewolves-backend to stage dev (us-west-2)

✔ Service deployed to stack werewolves-backend-dev (112s)

functions:
  startGame: werewolves-backend-play (1.5 kB)
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function startGame
```
