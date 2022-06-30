export WANDB_PROJECT=pol
TASK='case_hold'
SEED=1


MODEL='roberta-base'
MODEL_NAME_OR_PATH=${MODEL}



python tasks/casehold.py \
    --model_name_or_path ${MODEL_NAME_OR_PATH} \
    --task_name ${TASK} \
    --do_train \
    --do_eval \
    --evaluation_strategy='steps' \
    --eval_steps 500 \
    --save_strategy='steps' \
    --save_steps 0 \
    --logging_steps 500 \
    --max_seq_length 512 \
    --per_device_train_batch_size=2 \
    --per_device_eval_batch_size=64 \
    --learning_rate=1e-5 \
    --num_train_epochs=7 \
    --seed ${SEED} \
    --fp16 \
    --report_to=wandb \
    --run_name=${TASK}/${MODEL}/seed_${SEED} \
    --output_dir=logs/${TASK}/${MODEL}/lr=1e-5/seed_${SEED} \
    --overwrite_output_dir