#nullable enable
using System;
using Environment = System.Environment;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using Godot;

namespace Step1CSharpWeb;

public partial class ThreadProbe : Node
{
    private readonly Stopwatch _clock = new();
    private int _mainId;
    private int _threadId;
    private int _done;
    private long _result;
    private Task<(int Id, long Result)>? _task;
    private bool _reported;

    private static long Calculate()
    {
        long sum = 0;
        for (int i = 0; i < 500000; i++) sum += i;
        return sum;
    }

    public override void _Ready()
    {
        var random = new byte[32];
        System.Security.Cryptography.RandomNumberGenerator.Fill(random);
        if (Array.TrueForAll(random, value => value == 0))
            throw new InvalidOperationException("Browser cryptography returned no random data");
        GD.Print("BROWSER_CRYPTO_PASS");
        _mainId = Environment.CurrentManagedThreadId;
        GD.Print($"THREAD_PROBE_START main={_mainId}");
        _clock.Start();
        try
        {
            new System.Threading.Thread(() =>
            {
                _threadId = Environment.CurrentManagedThreadId;
                _result = Calculate();
                Volatile.Write(ref _done, 1);
            }) { IsBackground = true }.Start();
            _task = Task.Run(() => (Environment.CurrentManagedThreadId, Calculate()));
        }
        catch (Exception ex)
        {
            GD.Print($"THREAD_PROBE_FAIL {ex}");
            _reported = true;
        }
    }

    public override void _Process(double delta)
    {
        if (_reported) return;
        if (_task?.IsFaulted == true)
        {
            GD.Print($"THREAD_PROBE_FAIL {_task.Exception}");
            _reported = true;
        }
        else if (Volatile.Read(ref _done) == 1 && _task?.IsCompletedSuccessfully == true)
        {
            var task = _task.GetAwaiter().GetResult();
            var pass = _threadId != _mainId && task.Id != _mainId
                && _result == 124999750000L && task.Result == _result;
            GD.Print($"THREAD_PROBE_{(pass ? "PASS" : "FAIL")} main={_mainId} thread={_threadId} task={task.Id} sum={_result}");
            _reported = true;
        }
        else if (_clock.Elapsed.TotalSeconds > 30)
        {
            GD.Print("THREAD_PROBE_FAIL timeout");
            _reported = true;
        }
    }
}
